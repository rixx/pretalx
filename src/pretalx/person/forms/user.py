# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import hashlib
import ipaddress

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone, translation
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from pretalx.cfp.forms.cfp import CfPFormMixin
from pretalx.common.forms.fields import NewPasswordConfirmationField, NewPasswordField
from pretalx.common.forms.renderers import InlineFormLabelRenderer
from pretalx.common.http import get_client_ip
from pretalx.common.text.phrases import phrases
from pretalx.person.models import User


class UserForm(CfPFormMixin, forms.Form):
    default_renderer = InlineFormLabelRenderer

    login_email = forms.EmailField(
        max_length=60,
        label=phrases.base.enter_email,
        required=False,
        widget=forms.EmailInput(attrs={"autocomplete": "username"}),
    )
    login_password = forms.CharField(
        label=_("Password"),
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    register_name = forms.CharField(
        label=_("Name") + f" ({_('display name')})",
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    register_email = forms.EmailField(
        label=phrases.base.enter_email,
        required=False,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    register_password = NewPasswordField(
        label=_("Password"),
        required=False,
    )
    register_password_repeat = NewPasswordConfirmationField(
        label=_("Password (again)"),
        required=False,
        confirm_with="register_password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    FIELDS_ERROR = _(
        "Please fill all fields of either the login or the registration form."
    )
    RATE_LIMIT_ERROR = _(
        "For security reasons, please wait 5 minutes before you try again."
    )

    def __init__(self, *args, request=None, **kwargs):
        kwargs.pop("event", None)
        self.request = request
        super().__init__(*args, **kwargs)

    @cached_property
    def ratelimit_key(self):
        """Generate a rate limiting key based on the client IP address.

        Returns None if Redis is not available, if the client IP cannot be
        determined, or if the IP is private (indicating a misconfigured reverse proxy).
        """
        if not settings.HAS_REDIS:
            return None
        if not self.request:
            return None
        client_ip = get_client_ip(self.request)
        if not client_ip:
            return None
        try:
            client_ip = ipaddress.ip_address(client_ip)
        except ValueError:
            # Web server not set up correctly
            return None
        if client_ip.is_private:
            # This is the private IP of the server, web server not set up correctly
            return None
        return f"pretalx_login_{hashlib.sha1(str(client_ip).encode()).hexdigest()}"

    def _clean_login(self, data):
        # Check rate limit before attempting authentication
        if self.ratelimit_key:
            from django.core.cache import cache

            cnt = cache.get(self.ratelimit_key)
            if cnt and int(cnt) > 10:
                raise ValidationError(self.RATE_LIMIT_ERROR)

        try:
            uname = User.objects.get(email__iexact=data.get("login_email")).email
        except User.DoesNotExist:  # We do this to avoid timing attacks
            uname = "user@invalid"

        user = authenticate(username=uname, password=data.get("login_password"))

        if user is None:
            # Increment rate limit counter on failed authentication
            if self.ratelimit_key:
                from django.core.cache import cache

                cache_value = cache.get(self.ratelimit_key, 0)
                cache.set(self.ratelimit_key, int(cache_value) + 1, 300)

            raise ValidationError(
                _(
                    "No user account matches the entered credentials. "
                    "Are you sure that you typed your password correctly?"
                )
            )

        if not user.is_active:
            raise ValidationError(_("Sorry, your account is currently disabled."))

        data["user_id"] = user.pk

    def _clean_register(self, data):
        if data.get("register_password") != data.get("register_password_repeat"):
            self.add_error(
                "register_password_repeat",
                ValidationError(phrases.base.passwords_differ),
            )

        if User.objects.filter(email__iexact=data.get("register_email")).exists():
            self.add_error(
                "register_email",
                ValidationError(
                    _(
                        "We already have a user with that email address. Did you already register "
                        "before and just need to log in?"
                    )
                ),
            )

    def clean(self):
        data = super().clean()

        if data.get("login_email") and data.get("login_password"):
            self._clean_login(data)
        elif (
            data.get("register_email")
            and data.get("register_password")
            and data.get("register_name")
        ):
            self._clean_register(data)
        else:
            raise ValidationError(self.FIELDS_ERROR)

        return data

    def save(self):
        data = self.cleaned_data
        if data.get("login_email") and data.get("login_password"):
            return data["user_id"]

        # We already checked that all fields are filled, but sometimes
        # they end up empty regardless. No idea why and how.
        if not (
            data.get("register_email")
            and data.get("register_password")
            and data.get("register_name")
        ):
            raise ValidationError(self.FIELDS_ERROR)

        user = User.objects.create_user(
            name=data.get("register_name").strip(),
            email=data.get("register_email").lower().strip(),
            password=data.get("register_password"),
            locale=translation.get_language(),
            timezone=timezone.get_current_timezone_name(),
        )
        data["user_id"] = user.pk
        return user.pk

    class Media:
        css = {"all": ["common/css/forms/auth.css"]}
