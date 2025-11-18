# SPDX-FileCopyrightText: 2017-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from pathlib import Path

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from pretalx.agenda.rules import can_view_schedule, is_speaker_viewable
from pretalx.common.models.fields import MarkdownField
from pretalx.common.models.mixins import PretalxModel
from pretalx.common.text.path import path_with_hash
from pretalx.common.urls import EventUrls
from pretalx.orga.rules import can_view_speaker_names
from pretalx.person.rules import (
    can_mark_speakers_arrived,
    is_administrator,
    is_reviewer,
)
from pretalx.submission.rules import orga_can_change_submissions


def speaker_avatar_path(instance, filename):
    """Generate upload path for speaker profile avatars."""
    if instance.user and instance.user.code:
        extension = Path(filename).suffix
        filename = f"{instance.user.code}_{instance.event.slug}{extension}"
    return path_with_hash(filename, base_path="avatars")


class SpeakerProfile(PretalxModel):
    """All :class:`~pretalx.event.models.event.Event` related data concerning
    a.

    :class:`~pretalx.person.models.user.User` is stored here.

    :param has_arrived: Can be set to track speaker arrival. Will be used in
        warnings about missing speakers.
    :param avatar: Event-specific profile picture for this speaker.
    """

    user = models.ForeignKey(
        to="person.User",
        related_name="profiles",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    event = models.ForeignKey(
        to="event.Event", related_name="+", on_delete=models.CASCADE
    )
    biography = MarkdownField(
        verbose_name=_("Biography"),
        null=True,
        blank=True,
    )
    has_arrived = models.BooleanField(
        default=False, verbose_name=_("The speaker has arrived")
    )
    internal_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Internal notes"),
        help_text=_(
            "Internal notes for other organisers/reviewers. Not visible to the speakers or the public."
        ),
    )
    avatar = models.ImageField(
        null=True,
        blank=True,
        verbose_name=_("Profile picture"),
        upload_to=speaker_avatar_path,
        help_text=_(
            "Event-specific profile picture. Falls back to your global profile picture if not set."
        ),
    )
    avatar_thumbnail = models.ImageField(null=True, blank=True, upload_to="avatars/")
    avatar_thumbnail_tiny = models.ImageField(
        null=True, blank=True, upload_to="avatars/"
    )

    log_prefix = "pretalx.user.profile"

    class Meta:
        # These permissions largely apply to event-scoped user actions
        rules_permissions = {
            "list": can_view_schedule | (is_reviewer & can_view_speaker_names),
            "reviewer_list": is_reviewer & can_view_speaker_names,
            "orga_list": orga_can_change_submissions
            | (is_reviewer & can_view_speaker_names),
            "view": is_speaker_viewable
            | orga_can_change_submissions
            | (is_reviewer & can_view_speaker_names),
            "orga_view": orga_can_change_submissions
            | (is_reviewer & can_view_speaker_names),
            "create": is_administrator,
            "update": orga_can_change_submissions,
            "mark_arrived": orga_can_change_submissions & can_mark_speakers_arrived,
            "delete": is_administrator,
        }

    class urls(EventUrls):
        public = "{self.event.urls.base}speaker/{self.user.code}/"
        social_image = "{public}og-image"
        talks_ical = "{self.urls.public}talks.ics"

    class orga_urls(EventUrls):
        base = "{self.event.orga_urls.speakers}{self.user.code}/"
        password_reset = "{self.event.orga_urls.speakers}{self.user.code}/reset"
        toggle_arrived = (
            "{self.event.orga_urls.speakers}{self.user.code}/toggle-arrived"
        )
        send_mail = (
            "{self.event.orga_urls.compose_mails_sessions}?speakers={self.user.code}"
        )

    def __str__(self):
        """Help when debugging."""
        user = self.user.get_display_name() if self.user else None
        return f"SpeakerProfile(event={self.event.slug}, user={user})"

    @cached_property
    def code(self):
        return self.user.code

    @cached_property
    def guid(self):
        return self.user.guid

    @cached_property
    def name(self):
        """Backwards compatibility property to access user name."""
        return self.user.name if self.user else None

    @cached_property
    def submissions(self):
        """All non-deleted.

        :class:`~pretalx.submission.models.submission.Submission` objects for
        this speaker profile.
        """
        return self.event.submissions.filter(speaker_profiles=self)

    @cached_property
    def talks(self):
        """A queryset of.

        :class:`~pretalx.submission.models.submission.Submission` objects.

        Contains all visible talks for this speaker profile.
        """
        return self.event.talks.filter(speaker_profiles=self)

    @cached_property
    def answers(self):
        """A queryset of :class:`~pretalx.submission.models.question.Answer`
        objects.

        Includes all answers given for this speaker profile or for their talks.
        """
        from pretalx.submission.models import Answer

        return Answer.objects.filter(
            models.Q(submission__speaker_profiles=self) | models.Q(speaker_profile=self)
        ).order_by("question__position")

    @property
    def reviewer_answers(self):
        return self.answers.filter(question__is_visible_to_reviewers=True).order_by(
            "question__position"
        )

    def save(self, *args, **kwargs):
        """Save the profile and sync avatar with User if needed."""
        # If this profile has an avatar but the user doesn't, copy to user
        if self.avatar and self.user and not self.user.avatar:
            # Save the file to the user's avatar field without creating duplicates
            self.user.avatar = self.avatar
            self.user.save(update_fields=['avatar'])

        return super().save(*args, **kwargs)

    def get_avatar(self):
        """Get the avatar for this profile, falling back to user avatar."""
        if self.avatar:
            return self.avatar
        if self.user:
            return self.user.avatar
        return None

    @cached_property
    def avatar_url(self):
        """Get avatar URL, preferring profile avatar over user avatar."""
        if not self.event.cfp.request_avatar:
            return None

        avatar = self.get_avatar()
        if not avatar:
            return None

        from pretalx.common.image import create_thumbnail
        from urllib.parse import urljoin
        from django.conf import settings

        if self.event and self.event.custom_domain:
            return urljoin(self.event.custom_domain, avatar.url)
        return urljoin(settings.SITE_URL, avatar.url)

    def get_avatar_url(self, thumbnail=None):
        """Get avatar URL with optional thumbnail size."""
        avatar = self.get_avatar()
        if not avatar:
            return ""

        from pretalx.common.image import create_thumbnail
        from urllib.parse import urljoin
        from django.conf import settings

        if not thumbnail:
            image = avatar
        else:
            # Check if we have the thumbnail field on this model or user
            if self.avatar:
                thumb_field = (
                    self.avatar_thumbnail_tiny
                    if thumbnail == "tiny"
                    else self.avatar_thumbnail
                )
            else:
                thumb_field = (
                    self.user.avatar_thumbnail_tiny
                    if thumbnail == "tiny"
                    else self.user.avatar_thumbnail
                )

            if not thumb_field:
                image = create_thumbnail(avatar, thumbnail)
            else:
                image = thumb_field

        if not image:
            return ""

        if self.event and self.event.custom_domain:
            return urljoin(self.event.custom_domain, image.url)
        return urljoin(settings.SITE_URL, image.url)

    def _get_instance_data(self):
        data = {}
        if self.pk:
            avatar = self.get_avatar()
            data = {
                "name": self.user.name,
                "email": self.user.email,
                "avatar": avatar.name if avatar else None,
            }
        return super()._get_instance_data() | data
