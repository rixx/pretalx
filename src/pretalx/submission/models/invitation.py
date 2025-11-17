# SPDX-FileCopyrightText: 2017-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import string

from django.db import models
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from pretalx.common.models.mixins import PretalxModel
from pretalx.common.urls import build_absolute_uri


def generate_invite_token():
    return get_random_string(
        allowed_chars=string.ascii_lowercase + string.digits, length=32
    )


class SubmissionInvitation(PretalxModel):
    """A SubmissionInvitation tracks a pending invitation to become a speaker for a submission."""

    submission = models.ForeignKey(
        to="submission.Submission", related_name="invitations", on_delete=models.CASCADE
    )
    email = models.EmailField(verbose_name=_("Email"))
    token = models.CharField(
        default=generate_invite_token,
        max_length=64,
        null=True,
        blank=True,
        unique=True,
    )

    objects = models.Manager()

    class Meta:
        unique_together = (("submission", "email"),)

    def __str__(self) -> str:
        """Help with debugging."""
        return _("Invite to {submission} for {email}").format(
            submission=str(self.submission.title), email=self.email
        )

    @cached_property
    def event(self):
        return self.submission.event

    @cached_property
    def invitation_url(self):
        return build_absolute_uri(
            "cfp:invitation.view",
            kwargs={
                "event": self.event.slug,
                "code": self.submission.code,
                "invitation": self.token,
            },
        )

    def send(self, subject=None, text=None):
        from pretalx.mail.models import QueuedMail

        invitation_link = self.invitation_url

        if not text:
            invitation_text = _(
                """Hi!

You have been invited to be a speaker for the session "{title}" at {event}.

Please click here to accept the invitation:

{invitation_link}

See you there,
The {event} team"""
            ).format(
                title=str(self.submission.title),
                event=str(self.event.name),
                invitation_link=invitation_link,
            )
        else:
            invitation_text = text

        if not subject:
            invitation_subject = _("You have been invited as a speaker")
        else:
            invitation_subject = subject

        mail = QueuedMail.objects.create(
            event=self.event,
            to=self.email,
            subject=str(invitation_subject),
            text=str(invitation_text),
            locale=get_language(),
        )
        mail.send()
        return mail

    send.alters_data = True
