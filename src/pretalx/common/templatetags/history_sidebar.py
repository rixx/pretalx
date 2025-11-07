# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from django import template
from django.contrib.contenttypes.models import ContentType

from pretalx.common.models import ActivityLog

register = template.Library()


@register.inclusion_tag("common/history_sidebar.html", takes_context=True)
def history_sidebar(context, obj, limit=10):
    """Display compact history sidebar showing recent log entries for an object."""
    request = context.get("request")

    if not request or not hasattr(request, "user") or not request.user.is_authenticated:
        return {"log_entries": [], "show_history": False}

    if hasattr(obj, "logged_actions"):
        log_entries = obj.logged_actions()[:limit]
    else:
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
