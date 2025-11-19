# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import functools
import logging
import traceback

from django.conf import settings
from django.core.mail import mail_admins

logger = logging.getLogger(__name__)


def get_queue():
    """Get the RQ queue for background tasks.

    Returns None if no Redis URL is configured (tasks will run eagerly).
    """
    if not getattr(settings, "RQ_REDIS_URL", None):
        return None

    from redis import Redis
    from rq import Queue

    connection = Redis.from_url(settings.RQ_REDIS_URL)
    return Queue(connection=connection, default_timeout=600)


def execute_task(func, args, kwargs, task_info=None):
    """Execute a task and handle exceptions.

    Sends exception emails to admins on failure (in production).
    """
    try:
        return func(*args, **kwargs)
    except Exception as exception:
        if not settings.DEBUG and settings.ADMINS:
            if (
                settings.EMAIL_BACKEND
                != "django.core.mail.backends.locmem.EmailBackend"
            ):
                _send_exception_email(func, args, kwargs, exception, task_info)
        raise


def _send_exception_email(func, args, kwargs, exception, task_info=None):
    """Send an exception email to admins when a task fails."""
    from pretalx.common.exceptions import PretalxTaskExceptionReporter

    task_name = getattr(func, "_task_name", func.__name__)
    job_id = task_info.get("job_id") if task_info else None

    reporter = PretalxTaskExceptionReporter(
        request=None,
        exc_type=type(exception),
        exc_value=exception,
        tb=traceback.extract_tb(exception.__traceback__),
        is_email=True,
        task_id=job_id or task_name,
        task_args=(args, kwargs),
    )

    subject = f"[Django] ERROR (TASK): Internal Server Error: {task_name}"
    message = reporter.get_traceback_text()
    html_message = reporter.get_traceback_html()
    mail_admins(subject, message, fail_silently=True, html_message=html_message)


class Task:
    """A task that can be enqueued or run immediately.

    Similar to Celery's task but using RQ as the backend.
    """

    def __init__(self, func, name=None, bind=False):
        self.func = func
        self.name = name or func.__name__
        self.bind = bind
        self._task_name = name
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        """Run the task directly (synchronously)."""
        if self.bind:
            return self.func(TaskContext(), *args, **kwargs)
        return self.func(*args, **kwargs)

    def delay(self, *args, **kwargs):
        """Enqueue the task with positional and keyword arguments."""
        return self.apply_async(args=args, kwargs=kwargs)

    def apply_async(self, args=None, kwargs=None, ignore_result=True):
        """Enqueue the task for background execution.

        Falls back to eager execution if no queue is configured.
        """
        args = args or ()
        kwargs = kwargs or {}

        queue = get_queue()
        if queue is None:
            # Run eagerly if no queue configured
            return execute_task(self, args, kwargs)

        # Create a wrapper function that handles bind and exception reporting
        def task_wrapper(*args, **kwargs):
            bound_args = args
            if self.bind:
                context = TaskContext()
                context.job = kwargs.pop("_rq_job", None)
                return execute_task(
                    self.func, (context,) + bound_args, kwargs, {"job_id": self.name}
                )
            return execute_task(self.func, bound_args, kwargs, {"job_id": self.name})

        # Copy task metadata to wrapper
        task_wrapper._task_name = self.name

        return queue.enqueue(
            task_wrapper,
            *args,
            **kwargs,
            job_timeout=600,
            result_ttl=0 if ignore_result else 500,
        )


class TaskContext:
    """Context object passed to bound tasks (similar to Celery's self).

    Provides retry functionality and request information.
    """

    def __init__(self):
        self.job = None
        self._retries = 0

    @property
    def request(self):
        """Provide request-like object for compatibility."""
        return self

    @property
    def retries(self):
        """Get the current retry count."""
        if self.job:
            return self.job.meta.get("retries", 0)
        return self._retries

    def retry(self, max_retries=3, countdown=60, exc=None):
        """Retry the task with exponential backoff.

        Args:
            max_retries: Maximum number of retries
            countdown: Seconds to wait before retry
            exc: Exception that caused the retry (will be re-raised if max retries exceeded)
        """
        current_retries = self.retries

        if current_retries >= max_retries:
            if exc:
                raise exc
            raise MaxRetriesExceededError(
                f"Max retries ({max_retries}) exceeded for task"
            )

        queue = get_queue()
        if queue is None:
            # In eager mode, just raise the exception
            if exc:
                raise exc
            return

        # Get the current job and requeue it
        if self.job:
            self.job.meta["retries"] = current_retries + 1
            self.job.save_meta()
            # Requeue the job with the new retry count
            queue.enqueue_in(
                timedelta(seconds=countdown),
                self.job.func,
                *self.job.args,
                **self.job.kwargs,
                meta={"retries": current_retries + 1},
            )

        # Raise RetryTask to signal RQ to stop current execution
        raise RetryTask(f"Retrying task, attempt {current_retries + 1}")


class RetryTask(Exception):
    """Raised to signal that a task should be retried."""

    pass


class MaxRetriesExceededError(Exception):
    """Raised when a task exceeds its maximum retry count."""

    pass


def task(name=None, bind=False):
    """Decorator to define a background task.

    Args:
        name: Optional name for the task (defaults to function name)
        bind: If True, the task function receives a TaskContext as first argument

    Example:
        @task(name="myapp.my_task")
        def my_task(arg1, arg2):
            # Do work
            pass

        # Enqueue the task
        my_task.apply_async(kwargs={"arg1": "value1", "arg2": "value2"})

        @task(bind=True)
        def my_retryable_task(self, arg1):
            try:
                # Do work
                pass
            except SomeError:
                self.retry(max_retries=5, countdown=60)
    """

    def decorator(func):
        return Task(func, name=name, bind=bind)

    return decorator


# Import timedelta for retry functionality
from datetime import timedelta  # noqa: E402
