# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from django.conf import settings
from django.core.checks import INFO, WARNING, CheckMessage, register

CONFIG_HINT = "https://docs.pretalx.org/administrator/configure/"


@register()
def check_queue(app_configs, **kwargs):
    if app_configs:
        return []
    if settings.RQ_EAGER:
        if not settings.DEBUG:
            return [
                CheckMessage(
                    level=WARNING,
                    msg="There is no task runner (RQ) configured.",
                    hint=f"Task runners are recommended in production: {CONFIG_HINT}#the-redis-section",
                    id="pretalx.W001",
                )
            ]
        return []

    errors = []
    try:
        from redis import Redis

        connection = Redis.from_url(settings.RQ_REDIS_URL)
        connection.ping()
    except Exception as e:
        # Only warning, as the task runner may just still be starting up
        errors.append(
            CheckMessage(
                level=WARNING,
                msg="Could not connect to Redis for task queue",
                hint=str(e),
                id="pretalx.W002",
            )
        )
    return errors


@register(deploy=True)
def check_sqlite_in_production(app_configs, **kwargs):
    if app_configs:
        return []
    if settings.DATABASES["default"]["ENGINE"].endswith("sqlite3"):
        return [
            CheckMessage(
                level=INFO,
                msg="Running SQLite in production is not recommended.",
                id="pretalx.I001",
            )
        ]
    return []


@register(deploy=True)
def check_admin_email(app_configs, **kwargs):
    if app_configs:
        return []
    if not settings.ADMINS:
        return [
            CheckMessage(
                level=INFO,
                msg="You have not admin contact address configured and will not receive errors via email.",
                hint=f"{CONFIG_HINT}#the-logging-section",
                id="pretalx.I002",
            )
        ]
    return []


@register(deploy=True)
def check_system_email(app_configs, **kwargs):
    if app_configs:
        return []
    errors = []
    fields = ("EMAIL_HOST", "EMAIL_PORT", "MAIL_FROM")
    missing_fields = [field for field in fields if not getattr(settings, field)]
    if missing_fields:
        fields = ", ".join(missing_fields)
        errors.append(
            CheckMessage(
                level=WARNING,
                msg=f"Missing email configuration: {fields}",
                hint=f"{CONFIG_HINT}#the-mail-section",
                id="pretalx.W003",
            )
        )
    if settings.EMAIL_USE_TLS and settings.EMAIL_USE_SSL:
        errors.append(
            CheckMessage(
                level=ERROR,
                msg="Both EMAIL_USE_TLS and EMAIL_USE_SSL are set, but only one of the two may be set.",
                hint=f"{CONFIG_HINT}#the-mail-section",
                id="pretalx.E002",
            )
        )
    return []


@register(deploy=True)
def check_caches(app_configs, **kwargs):
    if app_configs:
        return []
    if not settings.HAS_REDIS:
        return [
            CheckMessage(
                level=INFO,
                msg="You have no Redis server configured, which is strongly recommended in production.",
                hint=f"{CONFIG_HINT}#the-redis-section",
                id="pretalx.I003",
            )
        ]
    return []


@register(deploy=True)
def check_debug(app_configs, **kwargs):
    if app_configs:
        return []
    errors = []
    if not settings.SITE_URL.startswith("https"):
        errors.append(
            CheckMessage(
                level=WARNING,
                msg="Your configured site does not start with https. Please run only https sites in production.",
                hint=f"{CONFIG_HINT}#the-site-section",
                id="pretalx.W004",
            )
        )
    if settings.DEBUG:
        # Overriding the default check in order to link our docs, and also to escalate
        # to level=ERROR.
        errors.append(
            CheckMessage(
                level=ERROR,
                msg="You are running in debug mode in deployment, this is a security risk!",
                hint=f"{CONFIG_HINT}#the-site-section",
                id="pretalx.W004",
            )
        )
    return errors
