# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from pretalx.common.forms.renderers import InlineFormRenderer


class EventHistoryFilterForm(forms.Form):
    """Filter form for event activity log history."""

    object_type = forms.ChoiceField(
        required=False,
        label=_("Object type"),
        widget=forms.Select(attrs={"title": _("Filter by object type")}),
    )
    action_type = forms.ChoiceField(
        required=False,
        label=_("Action type"),
        widget=forms.Select(attrs={"title": _("Filter by action type")}),
    )

    default_renderer = InlineFormRenderer

    # Map content type app_label.model to readable names
    CONTENT_TYPE_NAMES = {
        "submission.submission": _("Proposals"),
        "submission.question": _("Custom fields"),
        "submission.answerOption": _("Custom field options"),
        "submission.review": _("Reviews"),
        "submission.submissioncomment": _("Comments"),
        "submission.tag": _("Tags"),
        "submission.track": _("Tracks"),
        "submission.submissiontype": _("Proposal types"),
        "person.speakerprofile": _("Speakers"),
        "person.user": _("Users"),
        "mail.mailtemplate": _("Mail templates"),
        "mail.queuedmail": _("Emails"),
        "schedule.room": _("Rooms"),
        "schedule.schedule": _("Schedules"),
        "schedule.talkslot": _("Slots"),
        "event.event": _("Event"),
        "cfp.cfp": _("Call for Proposals"),
        "team.team": _("Teams"),
    }

    # Group action types by category for better UX
    ACTION_TYPE_GROUPS = {
        _("Proposals"): [
            ("pretalx.submission.create", _("Created")),
            ("pretalx.submission.update", _("Modified")),
            ("pretalx.submission.delete", _("Deleted")),
            ("pretalx.submission.deleted", _("Deleted")),
            ("pretalx.submission.accept", _("Accepted")),
            ("pretalx.submission.reject", _("Rejected")),
            ("pretalx.submission.cancel", _("Cancelled")),
            ("pretalx.submission.confirm", _("Confirmed")),
            ("pretalx.submission.withdraw", _("Withdrawn")),
        ],
        _("Custom fields"): [
            ("pretalx.question.create", _("Created")),
            ("pretalx.question.update", _("Modified")),
            ("pretalx.question.delete", _("Deleted")),
            ("pretalx.question.option.create", _("Option created")),
            ("pretalx.question.option.update", _("Option modified")),
            ("pretalx.question.option.delete", _("Option deleted")),
        ],
        _("Emails"): [
            ("pretalx.mail.create", _("Created")),
            ("pretalx.mail.update", _("Modified")),
            ("pretalx.mail.delete", _("Deleted")),
            ("pretalx.mail.sent", _("Sent")),
            ("pretalx.mail_template.create", _("Template created")),
            ("pretalx.mail_template.update", _("Template modified")),
            ("pretalx.mail_template.delete", _("Template deleted")),
        ],
        _("Schedule"): [
            ("pretalx.schedule.release", _("Released")),
            ("pretalx.room.create", _("Room created")),
            ("pretalx.room.update", _("Room modified")),
            ("pretalx.room.delete", _("Room deleted")),
        ],
        _("Event"): [
            ("pretalx.event.create", _("Created")),
            ("pretalx.event.update", _("Modified")),
            ("pretalx.event.activate", _("Activated")),
            ("pretalx.event.deactivate", _("Deactivated")),
            ("pretalx.cfp.update", _("CfP modified")),
        ],
    }

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

        # Build object type choices from existing logs
        if event:
            # Get distinct content types that have logs for this event
            from pretalx.common.models import ActivityLog

            content_type_ids = (
                ActivityLog.objects.filter(event=event)
                .values_list("content_type", flat=True)
                .distinct()
            )
            content_types = ContentType.objects.filter(id__in=content_type_ids)

            object_type_choices = [("", _("All object types"))]
            for ct in content_types:
                key = f"{ct.app_label}.{ct.model}"
                name = self.CONTENT_TYPE_NAMES.get(key, f"{ct.app_label} {ct.model}")
                object_type_choices.append((ct.id, name))

            object_type_choices.sort(key=lambda x: str(x[1]))
            self.fields["object_type"].choices = object_type_choices

            # Build action type choices from existing logs
            action_types = (
                ActivityLog.objects.filter(event=event)
                .values_list("action_type", flat=True)
                .distinct()
                .order_by("action_type")
            )

            # Build flat list of all actions with groups
            action_type_choices = [("", _("All action types"))]
            seen_actions = set()

            # Add grouped actions
            for group_name, actions in self.ACTION_TYPE_GROUPS.items():
                group_actions = []
                for action_type, label in actions:
                    if action_type in action_types:
                        group_actions.append((action_type, label))
                        seen_actions.add(action_type)
                if group_actions:
                    action_type_choices.append((str(group_name), group_actions))

            # Add ungrouped actions
            other_actions = []
            for action_type in action_types:
                if action_type not in seen_actions:
                    # Clean up action type for display
                    display_name = action_type.replace("pretalx.", "").replace(".", " ").title()
                    other_actions.append((action_type, display_name))

            if other_actions:
                action_type_choices.append((_("Other"), other_actions))

            self.fields["action_type"].choices = action_type_choices

    def filter_queryset(self, qs):
        """Apply filters to the queryset."""
        object_type = self.cleaned_data.get("object_type")
        if object_type:
            qs = qs.filter(content_type_id=object_type)

        action_type = self.cleaned_data.get("action_type")
        if action_type:
            qs = qs.filter(action_type=action_type)

        return qs

    class Media:
        css = {"all": ["orga/css/forms/search.css"]}
