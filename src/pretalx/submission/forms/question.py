# SPDX-FileCopyrightText: 2017-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from django import forms
from django.db.models import Q
from django.utils.functional import cached_property

from pretalx.cfp.forms.cfp import CfPFormMixin
from pretalx.common.forms.mixins import QuestionFieldsMixin
from pretalx.submission.models import Question, QuestionTarget, QuestionVariant


class QuestionsForm(CfPFormMixin, QuestionFieldsMixin, forms.Form):
    def __init__(self, *args, skip_limited_questions=False, **kwargs):
        self.event = kwargs.pop("event", None)
        self.submission = kwargs.pop("submission", None)
        self.speaker = kwargs.pop("speaker", None)
        self.review = kwargs.pop("review", None)
        self.track = kwargs.pop("track", None) or getattr(
            self.submission, "track", None
        )
        self.submission_type = kwargs.pop("submission_type", None) or getattr(
            self.submission, "submission_type", None
        )
        self.target_type = kwargs.pop("target", QuestionTarget.SUBMISSION)
        self.for_reviewers = kwargs.pop("for_reviewers", False)
        if self.target_type == QuestionTarget.SUBMISSION:
            target_object = self.submission
        elif self.target_type == QuestionTarget.SPEAKER:
            target_object = self.speaker
        elif self.target_type == QuestionTarget.REVIEWER:
            target_object = self.review
        else:
            target_object = self.speaker
        readonly = kwargs.pop("readonly", False)

        super().__init__(*args, **kwargs)

        self.queryset = Question.all_objects.filter(event=self.event, active=True)
        if self.target_type:
            self.queryset = self.queryset.filter(target=self.target_type)
        else:
            self.queryset = self.queryset.exclude(
                target=QuestionTarget.REVIEWER
            ).order_by("-target", "position")
        if skip_limited_questions:
            self.queryset = self.queryset.filter(
                tracks__isnull=True,
                submission_types__isnull=True,
            )
        else:
            if self.track:
                self.queryset = self.queryset.filter(
                    Q(tracks__in=[self.track]) | Q(tracks__isnull=True)
                )
            if self.submission_type:
                self.queryset = self.queryset.filter(
                    Q(submission_types__in=[self.submission_type])
                    | Q(submission_types__isnull=True)
                )
        if self.for_reviewers:
            self.queryset = self.queryset.filter(is_visible_to_reviewers=True)
        for question in self.queryset.prefetch_related("options"):
            initial_object = None
            initial = question.default_answer
            if target_object:
                answers = [
                    answer
                    for answer in target_object.answers.all()
                    if answer.question_id == question.id
                ]
                if answers:
                    initial_object = answers[0]
                    initial = (
                        answers[0].answer_file
                        if question.variant == QuestionVariant.FILE
                        else answers[0].answer
                    )

            field = self.get_field(
                question=question,
                initial=initial,
                initial_object=initial_object,
                readonly=readonly,
            )
            field.question = question
            field.answer = initial_object
            self.fields[f"question_{question.pk}"] = field

    @cached_property
    def speaker_fields(self):
        return [
            forms.BoundField(self, field, name)
            for name, field in self.fields.items()
            if field.question.target == QuestionTarget.SPEAKER
        ]

    @cached_property
    def submission_fields(self):
        return [
            forms.BoundField(self, field, name)
            for name, field in self.fields.items()
            if field.question.target == QuestionTarget.SUBMISSION
        ]

    def save(self):
        from pretalx.submission.models import QuestionTarget

        # Determine the parent object that should receive the log
        if self.target_type == QuestionTarget.SUBMISSION:
            parent_object = self.submission
        elif self.target_type == QuestionTarget.SPEAKER:
            parent_object = self.speaker
        elif self.target_type == QuestionTarget.REVIEWER:
            parent_object = self.review
        else:
            parent_object = None

        # Capture old state for all answers before making changes
        old_answers = {}
        for key, field in self.fields.items():
            if hasattr(field, 'question'):
                question = field.question
                if hasattr(field, 'answer') and field.answer:
                    old_answers[question.pk] = field.answer.answer_string
                else:
                    old_answers[question.pk] = None

        # Apply changes
        for key, value in self.cleaned_data.items():
            self.save_questions(key, value)

        # Collect changes by refreshing answers from parent object
        changes = {}
        if parent_object:
            # Refresh answers from DB to get the updated state
            parent_object.refresh_from_db()
            for key, field in self.fields.items():
                if not hasattr(field, 'question'):
                    continue

                question = field.question
                old_value = old_answers.get(question.pk)

                # Find the new answer from the parent object
                new_value = None
                for answer in parent_object.answers.all():
                    if answer.question_id == question.pk:
                        new_value = answer.answer_string
                        break

                # Check if there was a change
                if old_value != new_value:
                    question_label = str(question.question)
                    changes[question_label] = {
                        'old': old_value,
                        'new': new_value,
                    }

        # Log all changes as one entry on the parent object if there are any changes
        if changes and parent_object:
            parent_object.log_action(
                "pretalx.question.answer.update",
                data={'question_changes': changes},
                person=getattr(self, 'user', None),
                orga=getattr(self, 'is_orga', False),
            )
