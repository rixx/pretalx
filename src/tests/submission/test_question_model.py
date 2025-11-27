# SPDX-FileCopyrightText: 2017-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms
#
# This file contains Apache-2.0 licensed contributions copyrighted by the following contributors:
# SPDX-FileContributor: Natalia Katsiapi

import pytest
from django_scopes import scope

from pretalx.submission.models import Answer, Question


@pytest.mark.parametrize("target", ("submission", "speaker", "reviewer"))
@pytest.mark.django_db
def test_missing_answers_submission_question(submission, target, question):
    with scope(event=submission.event):
        assert question.missing_answers() == 1
        assert (
            question.missing_answers(filter_talks=submission.event.submissions.all())
            == 1
        )
        question.target = target
        question.save()
        if target == "submission":
            Answer.objects.create(
                answer="True", submission=submission, question=question
            )
        elif target == "speaker":
            Answer.objects.create(
                answer="True", person=submission.speakers.first(), question=question
            )
        assert question.missing_answers() == 0


@pytest.mark.django_db
def test_question_required_property_optional_questions(question):
    assert question.required is False


@pytest.mark.django_db
def test_question_required_property_always_required_questions(question_required_always):
    assert question_required_always.required is True


@pytest.mark.django_db
def test_question_required_property_required_after_option_before_deadline(
    question_required_after_option_before_deadline,
):
    assert question_required_after_option_before_deadline.required is False


@pytest.mark.django_db
def test_question_required_property_required_after_option_after_deadline(
    question_required_after_option_after_deadline,
):
    assert question_required_after_option_after_deadline.required is True


@pytest.mark.django_db
def test_question_required_property_freeze_after_option_before_deadline_question_required_optional(
    question_freeze_after_option_before_deadline_question_required_optional,
):
    assert (
        question_freeze_after_option_before_deadline_question_required_optional.required
        is False
    )


@pytest.mark.django_db
def test_question_required_property_freeze_after_option_after_deadline_question_required_optional(
    question_freeze_after_option_after_deadline_question_required_optional,
):
    assert (
        question_freeze_after_option_after_deadline_question_required_optional.required
        is False
    )


@pytest.mark.django_db
def test_question_required_property_freeze_after_option_after_deadline_question_required(
    question_freeze_after_option_after_deadline_question_required_required,
):
    assert (
        question_freeze_after_option_after_deadline_question_required_required.required
        is False
    )


@pytest.mark.django_db
def test_question_required_property_freeze_after_option_before_deadline_question_required(
    question_freeze_after_option_before_deadline_question_required_required,
):
    assert (
        question_freeze_after_option_before_deadline_question_required_required.required
        is True
    )


@pytest.mark.django_db
def test_question_property_freeze_after_option_after_deadline(
    question_freeze_after_option_after_deadline,
):
    assert question_freeze_after_option_after_deadline.read_only is True


@pytest.mark.django_db
def test_question_property_freeze_after_option_before_deadline(
    question_freeze_after_option_before_deadline,
):
    assert question_freeze_after_option_before_deadline.read_only is False


@pytest.mark.django_db
def test_question_base_properties(submission, question):
    a = Answer.objects.create(answer="True", submission=submission, question=question)
    assert a.event == question.event
    assert str(a.question.question) in str(a.question)
    assert str(a.question.question) in str(a)


@pytest.mark.parametrize(
    "variant,answer,expected",
    (
        ("number", "1", "1"),
        ("string", "hm", "hm"),
        ("text", "", ""),
        ("boolean", "True", "Yes"),
        ("boolean", "False", "No"),
        ("boolean", "None", ""),
        ("file", "answer", ""),
        ("choices", "answer", ""),
        ("lol", "lol", None),
    ),
)
@pytest.mark.django_db
def test_answer_string_property(event, variant, answer, expected):
    with scope(event=event):
        question = Question.objects.create(question="?", variant=variant, event=event)
        answer = Answer.objects.create(question=question, answer=answer)
        assert answer.answer_string == expected


@pytest.mark.django_db
def test_question_team_limits_no_limits(question, orga_user):
    """Test that users can see answers when no team limits are set."""
    assert question.user_can_see_answers(orga_user) is True


@pytest.mark.django_db
def test_question_team_limits_with_team_member(event, orga_user):
    """Test that team members can see answers to team-limited questions."""
    from pretalx.event.models import Team
    with scope(event=event):
        team = Team.objects.create(organiser=event.organiser, name="Test Team")
        team.members.add(orga_user)
        question = Question.objects.create(
            question="Team question", event=event, is_public=False
        )
        question.limit_teams.add(team)
        assert question.user_can_see_answers(orga_user) is True


@pytest.mark.django_db
def test_question_team_limits_non_team_member(event, orga_user):
    """Test that non-team members cannot see answers to team-limited questions."""
    from pretalx.event.models import Team
    from pretalx.person.models import User
    with scope(event=event):
        team = Team.objects.create(organiser=event.organiser, name="Test Team")
        question = Question.objects.create(
            question="Team question", event=event, is_public=False
        )
        question.limit_teams.add(team)
        other_user = User.objects.create(name="Other User", email="other@example.com")
        assert question.user_can_see_answers(other_user) is False


@pytest.mark.django_db
def test_question_team_limits_organizer_not_in_team(event, orga_user):
    """Test that even organizers cannot see answers if not in the team.

    Team limits are strictly enforced for sensitive data protection.
    """
    from pretalx.event.models import Team
    with scope(event=event):
        team = Team.objects.create(organiser=event.organiser, name="Test Team")
        # Don't add orga_user to the team
        question = Question.objects.create(
            question="Team question", event=event, is_public=False
        )
        question.limit_teams.add(team)
        # Even though orga_user has organizer permissions, they can't see answers
        assert question.user_can_see_answers(orga_user) is False


@pytest.mark.django_db
def test_filter_answers_by_team_access(event, submission, orga_user):
    """Test that filter_answers_by_team_access correctly filters answers."""
    from pretalx.event.models import Team
    from pretalx.submission.rules import filter_answers_by_team_access
    with scope(event=event):
        team = Team.objects.create(organiser=event.organiser, name="Test Team")
        team.members.add(orga_user)

        # Create a question with team limits
        team_question = Question.objects.create(
            question="Team Q", event=event, is_public=False
        )
        team_question.limit_teams.add(team)

        # Create a question without team limits
        public_question = Question.objects.create(
            question="Public Q", event=event, is_public=False
        )

        # Create answers
        team_answer = Answer.objects.create(
            question=team_question, submission=submission, answer="team"
        )
        public_answer = Answer.objects.create(
            question=public_question, submission=submission, answer="public"
        )

        # Test filtering
        all_answers = Answer.objects.filter(submission=submission)
        filtered = filter_answers_by_team_access(all_answers, orga_user)

        assert team_answer in filtered
        assert public_answer in filtered
