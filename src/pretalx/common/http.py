# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from django.conf import settings


def get_client_ip(request):
    """Get the client IP address from the request.

    Returns the client's IP address, considering X-Forwarded-For header
    if USE_X_FORWARDED_HOST is enabled in settings.
    """
    ip = request.META.get("REMOTE_ADDR")
    if settings.USE_X_FORWARDED_HOST:
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
    return ip
