# SPDX-FileCopyrightText: 2017-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from pretalx.common.text.phrases import phrases
from pretalx.mail.models import get_prefixed_subject
from pretalx.submission.models import SubmissionInvitation


class SubmissionInvitationForm(forms.Form):
    speaker = forms.EmailField(label=phrases.cfp.speaker_email)
    subject = forms.CharField(label=phrases.base.email_subject)
    text = forms.CharField(widget=forms.Textarea(), label=phrases.base.text_body)

    def __init__(self, submission, speaker, *args, **kwargs):
        self.submission = submission
        self.speaker = speaker
        initial = kwargs.get("initial", {})
        subject = phrases.cfp.invite_subject.format(speaker=speaker.get_display_name())
        initial["subject"] = get_prefixed_subject(submission.event, subject)

        # Create a temporary invitation to generate the URL
        temp_invitation = SubmissionInvitation(submission=submission)
        invitation_url = temp_invitation.invitation_url

        initial["text"] = phrases.cfp.invite_text.format(
            event=submission.event.name,
            title=submission.title,
            url=invitation_url,
            speaker=speaker.get_display_name(),
        )
        super().__init__(*args, **kwargs)

    def clean_speaker(self):
        email = self.cleaned_data["speaker"].strip().lower()

        # Check if user is already a speaker
        if self.submission.speakers.filter(email__iexact=email).exists():
            raise ValidationError(_("This person is already a speaker for this submission."))

        # Check if there's already a pending invitation
        if SubmissionInvitation.objects.filter(
            submission=self.submission, email__iexact=email
        ).exists():
            raise ValidationError(_("This person has already been invited."))

        # Check if max_speakers limit has been reached
        max_speakers = self.submission.event.cfp.fields.get("additional_speaker", {}).get("max_speakers")
        if max_speakers is not None:
            current_count = self.submission.speakers.count()
            pending_count = self.submission.invitations.count()
            total_count = current_count + pending_count
            if total_count >= max_speakers:
                raise ValidationError(
                    _("This proposal has reached the maximum number of speakers ({max_speakers}).").format(
                        max_speakers=max_speakers
                    )
                )

        return email

    def save(self):
        email = self.cleaned_data["speaker"]
        invitation = SubmissionInvitation.objects.create(
            submission=self.submission,
            email=email,
        )
        invitation.send(
            subject=self.cleaned_data["subject"],
            text=self.cleaned_data["text"],
        )
        return invitation
