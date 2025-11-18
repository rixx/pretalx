# SPDX-FileCopyrightText: 2018-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import datetime as dt
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.files.uploadedfile import UploadedFile
from django.forms import CharField, FileField, RegexField, ValidationError
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _
from django_scopes.forms import SafeModelChoiceField

from pretalx.common.forms.widgets import (
    AvailabilitiesWidget,
    ClearableBasenameFileInput,
    ColorPickerWidget,
    ImageInput,
    NamePartsWidget,
    PasswordConfirmationInput,
    PasswordStrengthInput,
)
from pretalx.common.names import PERSON_NAME_SCHEMES, REQUIRED_NAME_PARTS
from pretalx.common.templatetags.filesize import filesize

# Avoid circular import - import these lazily in methods that need them
# from pretalx.schedule.models import Availability, Room

IMAGE_EXTENSIONS = {
    ".png": ["image/png", ".png"],
    ".jpg": ["image/jpeg", ".jpg"],
    ".jpeg": ["image/jpeg", ".jpeg"],
    ".gif": ["image/gif", ".gif"],
    ".svg": ["image/svg+xml", ".svg"],
    ".webp": ["image/webp", ".webp"],
}


class NewPasswordField(CharField):
    default_validators = [validate_password]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", PasswordStrengthInput(render_value=False))
        super().__init__(*args, **kwargs)


class NewPasswordConfirmationField(CharField):
    def __init__(self, *args, **kwargs):
        confirm = kwargs.pop("confirm_with", None)
        kwargs.setdefault("widget", PasswordConfirmationInput(confirm_with=confirm))
        super().__init__(*args, **kwargs)


class SizeFileInput:
    """Takes the intended maximum upload size in bytes."""

    def __init__(self, *args, **kwargs):
        if "max_size" not in kwargs:  # Allow None, but only explicitly
            self.max_size = settings.FILE_UPLOAD_DEFAULT_LIMIT
        else:
            self.max_size = kwargs.pop("max_size")
        super().__init__(*args, **kwargs)
        self.size_warning = self.get_size_warning(self.max_size)
        self.original_help_text = (
            getattr(self, "original_help_text", "") or self.help_text
        )
        self.added_help_text = getattr(self, "added_help_text", "") + self.size_warning
        self.help_text = self.original_help_text + " " + self.added_help_text
        self.widget.attrs["data-maxsize"] = self.max_size
        self.widget.attrs["data-sizewarning"] = self.size_warning

    @staticmethod
    def get_size_warning(max_size=None, fallback=True):
        if not max_size and fallback:
            max_size = settings.FILE_UPLOAD_DEFAULT_LIMIT
        return _("Please do not upload files larger than {size}!").format(
            size=filesize(max_size)
        )

    def validate(self, value):
        super().validate(value)
        if (
            self.max_size
            and isinstance(value, UploadedFile)
            and value.size > self.max_size
        ):
            raise ValidationError(self.size_warning)


class ExtensionFileInput:
    widget = ClearableBasenameFileInput
    extensions = {}

    def __init__(self, *args, **kwargs):
        self.extensions = kwargs.pop("extensions", None) or self.extensions or {}
        super().__init__(*args, **kwargs)
        content_types = set()
        for ext in self.extensions.values():
            content_types.update(ext)
        content_types = ",".join(content_types)
        self.widget.attrs["accept"] = content_types

    def validate(self, value):
        super().validate(value)
        if value:
            filename = value.name
            extension = Path(filename).suffix.lower()
            if extension not in self.extensions.keys():
                raise ValidationError(
                    _(
                        "This filetype ({extension}) is not allowed, it has to be one of the following: "
                    ).format(extension=extension)
                    + ", ".join(self.extensions.keys())
                )


class SizeFileField(SizeFileInput, FileField):
    pass


class ExtensionFileField(ExtensionFileInput, SizeFileField):
    pass


class ImageField(ExtensionFileField):
    widget = ImageInput
    extensions = IMAGE_EXTENSIONS


class ColorField(RegexField):
    regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    max_length = 7
    widget = ColorPickerWidget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, regex=self.regex, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs["pattern"] = self.regex[1:-1]
        return attrs


class SubmissionTypeField(SafeModelChoiceField):
    """Only include duration in a submission type’s representation
    if the duration is not a required CfP field (in which case, showing
    the default duration would be misleading, as it’s never used)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # All shown submission types in a form should belong to one event,
        # particularly in the non-organizer area where this field is used,
        # so we can just cache the rendering decision between instances.
        self.show_duration = None

    def label_from_instance(self, obj):
        if self.show_duration is None:
            self.show_duration = not bool(obj.event.cfp.require_duration)
        if self.show_duration:
            return str(obj)
        return str(obj.name)


class AvailabilitiesField(CharField):
    widget = AvailabilitiesWidget
    default_error_messages = {
        "invalid_json": _("Submitted availabilities are not valid json: %(error)s."),
        "invalid_format": _(
            "Availability JSON does not comply with expected format: %(detail)s"
        ),
        "invalid_availability_format": _(
            "The submitted availability does not comply with the required format."
        ),
        "invalid_date": _("The submitted availability contains an invalid date."),
        "required_availability": _("Please fill in your availability!"),
    }

    def __init__(self, *args, event=None, instance=None, resolution=None, **kwargs):
        self.event = event
        self.instance = instance
        self.resolution = resolution

        if "initial" not in kwargs and self.instance and self.event:
            kwargs["initial"] = self._serialize(self.event, self.instance)

        super().__init__(*args, **kwargs)

    def set_initial_from_instance(self):
        if self.event and not self.initial:
            self.initial = self._serialize(self.event, self.instance)

    def _serialize(self, event, instance):
        from pretalx.schedule.models import Availability, Room

        availabilities = []
        if instance and instance.pk:
            availabilities = [av.serialize() for av in instance.availabilities.all()]

        result = {
            "availabilities": [
                avail for avail in availabilities if avail["end"] > avail["start"]
            ],
            "event": {
                "timezone": event.timezone,
                "date_from": str(event.date_from),
                "date_to": str(event.date_to),
            },
        }
        if self.resolution:
            result["resolution"] = self.resolution
        if event and self.instance and not isinstance(self.instance, Room):
            # Speakers are limited to room availabilities, if any exist
            room_avails = event.availabilities.filter(room__isnull=False)
            if room_avails:
                merged_avails = Availability.union(room_avails)
                result["constraints"] = [
                    {
                        "start": avail.start.astimezone(event.tz).isoformat(),
                        "end": avail.end.astimezone(event.tz).isoformat(),
                    }
                    for avail in merged_avails
                ]

        return json.dumps(result)

    def _parse_availabilities_json(self, jsonavailabilities):
        try:
            rawdata = json.loads(jsonavailabilities)
        except ValueError as e:
            raise ValidationError(
                self.error_messages["invalid_json"],
                code="invalid_json",
                params={"error": e},
            )
        if not isinstance(rawdata, dict):
            raise ValidationError(
                self.error_messages["invalid_format"],
                code="invalid_format",
                params={"detail": f"Should be object, but is {type(rawdata)}"},
            )
        availabilities = rawdata.get("availabilities")
        if not isinstance(availabilities, list):
            raise ValidationError(
                self.error_messages["invalid_format"],
                code="invalid_format",
                params={
                    "detail": f"`availabilities` should be a list, but is {type(availabilities)}"
                },
            )
        return availabilities

    def _parse_datetime(self, strdate):
        obj = parse_datetime(strdate)
        if not obj:
            raise TypeError
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=self.event.tz)
        return obj

    def _validate_availability(self, rawavail):
        if not isinstance(rawavail, dict):
            raise ValidationError(
                self.error_messages["invalid_availability_format"],
                code="invalid_availability_format",
            )
        rawavail.pop("id", None)
        rawavail.pop("allDay", None)
        if set(rawavail.keys()) != {"start", "end"}:
            raise ValidationError(
                self.error_messages["invalid_availability_format"],
                code="invalid_availability_format",
            )

        try:
            for key in ("start", "end"):
                raw_value = rawavail[key]
                if not isinstance(raw_value, dt.datetime):
                    rawavail[key] = self._parse_datetime(raw_value)
        except (TypeError, ValueError):
            raise ValidationError(
                self.error_messages["invalid_date"], code="invalid_date"
            )

        timeframe_start = dt.datetime.combine(
            self.event.date_from, dt.time(), tzinfo=self.event.tz
        )
        if rawavail["start"] < timeframe_start:
            rawavail["start"] = timeframe_start

        timeframe_end = dt.datetime.combine(
            self.event.date_to, dt.time(), tzinfo=self.event.tz
        )
        timeframe_end = timeframe_end + dt.timedelta(days=1)
        rawavail["end"] = min(rawavail["end"], timeframe_end)

    def clean(self, value):
        from pretalx.schedule.models import Availability

        if isinstance(value, list):
            value = {"availabilities": value}
        if isinstance(value, dict):
            value = json.dumps(value)
        value = super().clean(value)
        if not value:
            if self.required:
                raise ValidationError(
                    self.error_messages["required_availability"],
                    code="required_availability",
                )
            return []

        rawavailabilities = self._parse_availabilities_json(value)
        availabilities = []

        for rawavail in rawavailabilities:
            self._validate_availability(rawavail)
            availabilities.append(Availability(event_id=self.event.id, **rawavail))

        if not availabilities and self.required:
            raise ValidationError(
                self.error_messages["required_availability"],
                code="required_availability",
            )

        return Availability.union(availabilities)


class NamePartsFormField(CharField):
    """Form field for structured name input based on event name scheme."""

    default_error_messages = {
        "invalid_json": _("Submitted name data is not valid: %(error)s."),
        "required_field": _("Please fill in the %(field)s field."),
    }

    def __init__(self, *args, event=None, scheme=None, **kwargs):
        self.event = event

        # Determine scheme from event settings or use default
        if scheme:
            self.scheme = scheme
        elif event:
            self.scheme = event.display_settings.get("name_scheme", "given_family")
        else:
            self.scheme = "given_family"

        # Set up the widget
        kwargs.setdefault("widget", NamePartsWidget(scheme=self.scheme))

        # Set label based on scheme
        if "label" not in kwargs:
            kwargs["label"] = _("Name")

        super().__init__(*args, **kwargs)

    def clean(self, value):
        """Validate and clean the name parts data."""
        # Parse JSON if it's a string
        if isinstance(value, str):
            if not value or value == "{}":
                if self.required:
                    raise ValidationError(
                        self.error_messages["required_field"],
                        code="required_field",
                        params={"field": _("name")},
                    )
                return {}

            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError) as e:
                raise ValidationError(
                    self.error_messages["invalid_json"],
                    code="invalid_json",
                    params={"error": str(e)},
                )

        if not isinstance(value, dict):
            value = {}

        # Validate required fields based on scheme
        if self.required and value:
            scheme_data = PERSON_NAME_SCHEMES.get(
                self.scheme, PERSON_NAME_SCHEMES["given_family"]
            )
            for field_name, label, _ in scheme_data["fields"]:
                if field_name in REQUIRED_NAME_PARTS and not value.get(field_name):
                    raise ValidationError(
                        self.error_messages["required_field"],
                        code="required_field",
                        params={"field": str(label)},
                    )

        # Ensure scheme is stored in the value
        if value and "_scheme" not in value:
            value["_scheme"] = self.scheme

        return value

    def prepare_value(self, value):
        """Prepare the value for display in the widget."""
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return json.dumps(value)
        return ""
