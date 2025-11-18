# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import rules

from pretalx.orga.rules import can_view_speaker_names
from pretalx.person.rules import is_reviewer
from pretalx.submission.rules import (
    are_featured_submissions_visible,
    is_speaker,
    orga_can_change_submissions,
)


def is_submission_visible_via_featured(user, submission):
    return bool(
        submission
        and submission.is_featured
        and are_featured_submissions_visible(user, submission.event)
    )


def is_submission_visible_via_schedule(user, submission):
    return bool(
        submission
        and submission.pk
        and is_agenda_visible(user, submission.event)
        and (submission.slot and submission.slot.is_visible)
    )


@rules.predicate
def is_agenda_visible(user, event):
    event = event.event
    return bool(
        event
        and event.is_public
        and event.get_feature_flag("show_schedule")
        and event.current_schedule
    )


can_view_schedule = (
    is_agenda_visible
    | orga_can_change_submissions
    | (is_reviewer & can_view_speaker_names)
)


@rules.predicate
def is_agenda_submission_visible(user, submission):
    submission = getattr(submission, "submission", submission)
    if not submission:
        return False
    return is_submission_visible_via_schedule(
        user, submission
    ) or is_submission_visible_via_featured(user, submission)


@rules.predicate
def is_viewable_profile(user, profile):
    """Check if a speaker profile should be viewable.

    A profile is viewable if the speaker has at least one visible submission
    (either via schedule or via featured).
    """
    # Get all submissions for this speaker in this event
    submissions = profile.event.submissions.filter(speaker_profiles=profile)

    # Check if any submission is visible
    for submission in submissions:
        if is_submission_visible_via_schedule(user, submission) or is_submission_visible_via_featured(user, submission):
            return True

    return False


is_speaker_viewable = is_viewable_profile & can_view_schedule


@rules.predicate
def is_widget_always_visible(user, event):
    return event.get_feature_flag("show_widget_if_not_public")


is_widget_visible = is_agenda_visible | is_widget_always_visible


@rules.predicate
def event_uses_feedback(user, event):
    event = getattr(event, "event", event)
    return event and event.get_feature_flag("use_feedback")
