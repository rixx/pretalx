# SPDX-FileCopyrightText: 2017-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms
#
# This file contains Apache-2.0 licensed contributions copyrighted by the following contributors:
# SPDX-FileContributor: Natalia Katsiapi

import pytest
from django_scopes import scope

from pretalx.common.forms.mixins import ALL_FILE_TYPES, QuestionFieldsMixin
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
def test_question_allowed_file_types_default(event):
    """Test that allowed_file_types defaults to an empty list."""
    with scope(event=event):
        question = Question.objects.create(
            question="Upload a file", variant="file", event=event
        )
        assert question.allowed_file_types == []


@pytest.mark.django_db
def test_question_allowed_file_types_can_be_set(event):
    """Test that allowed_file_types can be set and persisted."""
    with scope(event=event):
        question = Question.objects.create(
            question="Upload a file",
            variant="file",
            event=event,
            allowed_file_types=[".pdf", ".docx"],
        )
        assert question.allowed_file_types == [".pdf", ".docx"]

        # Verify it persists
        question.refresh_from_db()
        assert question.allowed_file_types == [".pdf", ".docx"]


@pytest.mark.django_db
def test_question_file_field_uses_all_types_when_no_restriction(event):
    """Test that file upload fields allow all types when no restriction is set."""
    with scope(event=event):
        question = Question.objects.create(
            question="Upload a file", variant="file", event=event
        )

        # Create a mixin instance to test get_field
        class TestMixin(QuestionFieldsMixin):
            pass

        mixin = TestMixin()
        mixin.event = event
        field = mixin.get_field(
            question=question, initial=None, initial_object=None, readonly=False
        )

        # Should allow all file types
        assert field.extensions == ALL_FILE_TYPES


@pytest.mark.django_db
def test_question_file_field_uses_restricted_types(event):
    """Test that file upload fields only allow specified types when restriction is set."""
    with scope(event=event):
        question = Question.objects.create(
            question="Upload a file",
            variant="file",
            event=event,
            allowed_file_types=[".pdf", ".docx"],
        )

        # Create a mixin instance to test get_field
        class TestMixin(QuestionFieldsMixin):
            pass

        mixin = TestMixin()
        mixin.event = event
        field = mixin.get_field(
            question=question, initial=None, initial_object=None, readonly=False
        )

        # Should only allow .pdf and .docx
        assert ".pdf" in field.extensions
        assert ".docx" in field.extensions
        assert ".png" not in field.extensions
        assert ".jpg" not in field.extensions
