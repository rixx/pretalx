# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from rest_framework.serializers import (
    CharField,
    DateTimeField,
    IntegerField,
    JSONField,
    SerializerMethodField,
)

from pretalx.api.mixins import PretalxSerializer
from pretalx.api.versions import CURRENT_VERSIONS, register_serializer
from pretalx.common.models import ActivityLog


@register_serializer(versions=CURRENT_VERSIONS)
class ActivityLogSerializer(PretalxSerializer):
    """Serializer for ActivityLog entries.

    Provides read-only access to activity log data for API consumers.
    Includes timestamp, person, action type, and change data.
    """

    id = IntegerField(read_only=True)
    timestamp = DateTimeField(read_only=True)
    action_type = CharField(read_only=True)
    is_orga_action = SerializerMethodField()
    person = SerializerMethodField()
    display = SerializerMethodField()
    data = JSONField(read_only=True, source="json_data")

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "timestamp",
            "action_type",
            "is_orga_action",
            "person",
            "display",
            "data",
        ]

    def get_is_orga_action(self, obj):
        """Return whether this was an organizer action."""
        return obj.is_orga_action

    def get_person(self, obj):
        """Return person information if available."""
        if obj.person:
            return {
                "code": obj.person.code,
                "name": obj.person.get_display_name(),
                "email": obj.person.email if self.context.get("include_email") else None,
            }
        return None

    def get_display(self, obj):
        """Return the human-readable display text for this log entry."""
        return obj.display
