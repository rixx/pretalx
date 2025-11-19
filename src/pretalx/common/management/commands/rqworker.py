# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run an RQ worker to process background tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--burst",
            action="store_true",
            default=False,
            help="Run in burst mode (quit after all jobs are done)",
        )
        parser.add_argument(
            "--with-scheduler",
            action="store_true",
            default=False,
            help="Run the scheduler alongside the worker for scheduled jobs",
        )

    def handle(self, *args, **options):
        if not settings.RQ_REDIS_URL:
            raise CommandError(
                "No Redis URL configured. Set the [redis] location in your config file."
            )

        from redis import Redis
        from rq import Worker

        connection = Redis.from_url(settings.RQ_REDIS_URL)

        worker_kwargs = {
            "connection": connection,
        }

        if options["with_scheduler"]:
            worker_kwargs["with_scheduler"] = True

        worker = Worker(["default"], **worker_kwargs)

        self.stdout.write(
            self.style.SUCCESS(f"Starting RQ worker connected to {settings.RQ_REDIS_URL}")
        )

        if options["burst"]:
            worker.work(burst=True)
        else:
            worker.work()
