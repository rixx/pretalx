# SPDX-FileCopyrightText: 2017-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from contextlib import suppress

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, models
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_scopes import ScopedManager, scopes_disabled
from rules.contrib.models import RulesModelBase, RulesModelMixin

SENSITIVE_KEYS = ["password", "secret", "api_key"]


class TimestampedModel(models.Model):
    created = models.DateTimeField(
        verbose_name=_("Created"), auto_now_add=True, blank=True, null=True
    )
    updated = models.DateTimeField(
        verbose_name=_("Updated"), auto_now=True, blank=True, null=True
    )

    class Meta:
        abstract = True


class LogMixin:
    log_prefix = None
    log_parent = None

    def log_action(
        self, action, data=None, person=None, orga=False, content_object=None, old_data=None, new_data=None
    ):
        if not self.pk or not isinstance(self.pk, int):
            return

        if action.startswith("."):
            if self.log_prefix:
                action = f"{self.log_prefix}{action}"
            else:
                return

        # If old_data and new_data are provided, compute changes
        if old_data is not None and new_data is not None:
            changes = self._compute_changes(old_data, new_data)
            if not changes and not data:
                # No changes detected and no explicit data, skip logging
                return
            if changes:
                # Store changes in the data dict
                if data is None:
                    data = {}
                data["changes"] = changes

        if data:
            if not isinstance(data, dict):
                raise TypeError(
                    f"Logged data should always be a dictionary, not {type(data)}."
                )
            for key, value in data.items():
                if any(sensitive_key in key for sensitive_key in SENSITIVE_KEYS):
                    value = data[key]
                    data[key] = "********" if value else value

        from pretalx.common.models import ActivityLog
        import json
        import logging

        # Test if data can be JSON serialized before attempting to create the log
        if data is not None:
            try:
                json.dumps(data)
            except (TypeError, ValueError) as e:
                # If JSON serialization fails, log warning and create without data
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Failed to serialize data for {action} on {type(self).__name__}: {e}. "
                    "Logging without detailed data."
                )
                data = None

        return ActivityLog.objects.create(
            event=getattr(self, "event", None),
            person=person,
            content_object=content_object or self,
            action_type=action,
            data=data,
            is_orga_action=orga,
        )

    def _compute_changes(self, old_data, new_data):
        """Compute changes between old and new data dictionaries.

        Returns a dict of changes in the format:
        {"field_name": {"old": old_value, "new": new_value}}
        """
        changes = {}

        # Check all fields that exist in either old or new data
        all_keys = set(old_data.keys()) | set(new_data.keys())

        for key in all_keys:
            old_value = old_data.get(key)
            new_value = new_data.get(key)

            # Skip if values are the same
            if old_value == new_value:
                continue

            changes[key] = {
                "old": old_value,
                "new": new_value
            }

        return changes

    def _make_json_serializable(self, value):
        """Recursively ensure a value is JSON serializable."""
        import json
        from decimal import Decimal

        # Import LazyI18nString to check for it
        try:
            from i18nfield.strings import LazyI18nString
            if isinstance(value, LazyI18nString):
                return str(value)
        except ImportError:
            pass

        if value is None:
            return None
        elif isinstance(value, Decimal):
            return str(value)
        elif isinstance(value, dict):
            return {k: self._make_json_serializable(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._make_json_serializable(v) for v in value]
        elif isinstance(value, (str, int, float, bool)):
            return value
        else:
            # For any other type, try JSON serialization test
            try:
                json.dumps(value)
                return value
            except (TypeError, ValueError):
                # If it can't be serialized, convert to string
                return str(value)

    def _get_instance_data(self):
        """Get a dictionary of field values for this instance.

        Used for change tracking in log_action. Excludes auto-updated
        fields like timestamps and sensitive data.
        """
        from decimal import Decimal
        from django.db import models
        from i18nfield.fields import I18nCharField, I18nTextField

        data = {}
        excluded_fields = {'created', 'updated', 'password'}

        for field in self._meta.fields:
            if field.name in excluded_fields:
                continue

            # Skip auto-generated or auto-updated fields
            if getattr(field, 'auto_now', False) or getattr(field, 'auto_now_add', False):
                continue

            value = getattr(self, field.name, None)

            # Handle special field types
            if isinstance(field, (I18nCharField, I18nTextField)):
                # I18n fields have a .data attribute that contains the dict
                if hasattr(value, 'data'):
                    # Recursively ensure the dict is JSON serializable
                    data[field.name] = self._make_json_serializable(value.data)
                else:
                    data[field.name] = str(value) if value is not None else None
            elif isinstance(field, models.ForeignKey):
                # Store foreign key as ID
                if value is not None:
                    data[field.name] = value.pk
                else:
                    data[field.name] = None
            elif isinstance(field, models.FileField):
                # Store file field as name/path
                if value:
                    data[field.name] = value.name
                else:
                    data[field.name] = None
            elif hasattr(field, 'choices') and field.choices:
                # CharField/IntegerField with choices - store the actual value, not the display value
                # This avoids LazyI18nString issues from _() translated choice display values
                data[field.name] = value
            else:
                # For other fields, ensure JSON serializability
                data[field.name] = self._make_json_serializable(value)

        # Note: ManyToMany fields are excluded as they are handled separately
        # and their changes are typically logged via through model changes

        return data

    def logged_actions(self):
        from pretalx.common.models import ActivityLog

        return (
            ActivityLog.objects.filter(
                content_type=ContentType.objects.get_for_model(type(self)),
                object_id=self.pk,
            )
            .select_related("event", "person")
            .prefetch_related("content_object")
        )

    def delete(self, *args, log_kwargs=None, **kwargs):
        parent = self.log_parent
        result = super().delete(*args, **kwargs)
        if parent and getattr(parent, "log_action", None) and self.log_prefix:
            log_kwargs = log_kwargs or {}
            parent.log_action(f"{self.log_prefix}.delete", **log_kwargs)
        return result


class FileCleanupMixin:
    """Deletes all uploaded files when object is deleted."""

    @cached_property
    def _file_fields(self):
        return [
            field.name
            for field in self._meta.fields
            if isinstance(field, models.FileField)
        ]

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        if not self.pk or (
            update_fields and not set(self._file_fields) & set(update_fields)
        ):
            return super().save(*args, **kwargs)

        try:
            pre_save_instance = self.__class__.objects.get(pk=self.pk)
        except Exception:
            return super().save(*args, **kwargs)

        for field in self._file_fields:
            if old_value := getattr(pre_save_instance, field):
                new_value = getattr(self, field)
                if new_value and old_value.path != new_value.path:
                    # We don't want to delete the file immediately, as the save action
                    # that triggered this task might still fail, so we schedule the
                    # deletion for 10 seconds in the future, and pass the file field
                    # to check if the file is still in use.
                    from pretalx.common.tasks import task_cleanup_file

                    task_cleanup_file.apply_async(
                        kwargs={
                            "model": str(self._meta.model_name.capitalize()),
                            "pk": self.pk,
                            "field": field,
                            "path": old_value.path,
                        },
                        countdown=10,
                    )
        return super().save(*args, **kwargs)

    def _delete_files(self):
        for field in self._file_fields:
            value = getattr(self, field, None)
            if value:
                with suppress(Exception):
                    value.delete(save=False)

    def delete(self, *args, **kwargs):
        self._delete_files()
        return super().delete(*args, **kwargs)

    def process_image(self, field, generate_thumbnail=False):
        from pretalx.common.tasks import task_process_image

        task_process_image.apply_async(
            kwargs={
                "field": field,
                "model": str(self._meta.model_name.capitalize()),
                "pk": self.pk,
                "generate_thumbnail": generate_thumbnail,
            },
            countdown=10,
        )


class PretalxModel(
    LogMixin,
    TimestampedModel,
    FileCleanupMixin,
    RulesModelMixin,
    models.Model,
    metaclass=RulesModelBase,
):
    """
    Base model for most pretalx models. Suitable for plugins.
    """

    objects = ScopedManager(event="event")

    class Meta:
        abstract = True


class GenerateCode:
    """Generates a random code on first save.

    Omits some character pairs because they are hard to
    read/differentiate: 1/I, O/0, 2/Z, 4/A, 5/S, 6/G.
    """

    _code_length = 6
    _code_charset = list("ABCDEFGHJKLMNPQRSTUVWXYZ3789")
    _code_property = "code"

    @classmethod
    def generate_code(cls, length=None):
        length = length or cls._code_length
        return get_random_string(length=length, allowed_chars=cls._code_charset)

    def assign_code(self, length=None):
        length = length or self._code_length
        while True:
            code = self.generate_code(length=length)
            with scopes_disabled():
                if not self.__class__.objects.filter(
                    **{f"{self._code_property}__iexact": code}
                ).exists():
                    setattr(self, self._code_property, code)
                    return

    def save(self, *args, **kwargs):
        # It’s super duper unlikely for this to fail, but let’s add a short
        # stupid retry loop regardless
        for __ in range(3):
            if not getattr(self, self._code_property, None):
                self.assign_code()
            try:
                return super().save(*args, **kwargs)
            except IntegrityError:
                setattr(self, self._code_property, None)


class OrderedModel:
    """Provides methods to move a model up and down in a queryset.

    Implement the `get_order_queryset` method as a classmethod or staticmethod
    to provide the queryset to order.
    """

    order_field = "position"
    order_up_url = "urls.up"
    order_down_url = "urls.down"

    @staticmethod
    def get_order_queryset(**kwargs):
        raise NotImplementedError

    def _get_attribute(self, attribute):
        result = self
        for part in attribute.split("."):
            result = getattr(result, part)
        return result

    def get_down_url(self):
        return self._get_attribute(self.order_down_url)

    def get_up_url(self):
        return self._get_attribute(self.order_up_url)

    def up(self):
        return self._move(up=True)

    def down(self):
        return self._move(up=False)

    @property
    def order_queryset(self):
        return self.get_order_queryset(event=self.event)

    def move(self, up=True):
        queryset = list(self.order_queryset.order_by(self.order_field))
        index = queryset.index(self)
        if index != 0 and up:
            queryset[index - 1], queryset[index] = queryset[index], queryset[index - 1]
        elif index != len(queryset) - 1 and not up:
            queryset[index + 1], queryset[index] = queryset[index], queryset[index + 1]

        for index, element in enumerate(queryset):
            if element.position != index:
                element.position = index
                element.save()

    move.alters_data = True
