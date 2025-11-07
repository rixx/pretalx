# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from django import template
from django.contrib.contenttypes.models import ContentType

from pretalx.common.models import ActivityLog

register = template.Library()


@register.inclusion_tag("common/history_sidebar.html", takes_context=True)
def history_sidebar(context, obj, limit=10):
    """Display a compact history sidebar for an object.

    Args:
        obj: The object to show history for (must have logged_actions method or be a model instance)
        limit: Maximum number of log entries to show (default: 10)

    Returns:
        Context dict with log entries for rendering the sidebar template
    """
    request = context.get("request")

    # Check if user has permission to view history
    # For now, we'll check if the user is an organizer (has orga permissions)
    if not request or not hasattr(request, "user") or not request.user.is_authenticated:
        return {"log_entries": [], "show_history": False}

    # Check if object has logged_actions method (from LogMixin)
    if hasattr(obj, "logged_actions"):
        log_entries = obj.logged_actions()[:limit]
    else:
        # Fallback: query ActivityLog directly using content type
        content_type = ContentType.objects.get_for_model(obj.__class__)
        log_entries = ActivityLog.objects.filter(
            content_type=content_type,
            object_id=obj.pk
        ).select_related("event", "person")[:limit]

    return {
        "log_entries": log_entries,
        "show_history": True,
        "object": obj,
        "request": request,
    }
