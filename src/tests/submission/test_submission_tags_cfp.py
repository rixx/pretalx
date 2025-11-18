# SPDX-FileCopyrightText: 2017-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import pytest
from django.core.exceptions import ValidationError
from django_scopes import scope

from pretalx.submission.forms import InfoForm
from pretalx.submission.models import SubmissionType, Tag


@pytest.mark.django_db
def test_tags_field_not_shown_when_do_not_ask(event, user):
    """Test that tags field is not shown when visibility is 'do_not_ask'."""
    with scope(event=event):
        event.cfp.fields["tags"]["visibility"] = "do_not_ask"
        event.cfp.save()

        form = InfoForm(event=event)
        assert "tags" not in form.fields


@pytest.mark.django_db
def test_tags_field_shown_when_optional(event, user):
    """Test that tags field is shown and optional when visibility is 'optional'."""
    with scope(event=event):
        Tag.objects.create(event=event, tag="Test Tag", is_public=True)
        event.cfp.fields["tags"]["visibility"] = "optional"
        event.cfp.save()

        form = InfoForm(event=event)
        assert "tags" in form.fields
        assert not form.fields["tags"].required


@pytest.mark.django_db
def test_tags_field_required_when_required(event, user):
    """Test that tags field is required when visibility is 'required'."""
    with scope(event=event):
        Tag.objects.create(event=event, tag="Test Tag", is_public=True)
        event.cfp.fields["tags"]["visibility"] = "required"
        event.cfp.save()

        form = InfoForm(event=event)
        assert "tags" in form.fields
        assert form.fields["tags"].required


@pytest.mark.django_db
def test_only_public_tags_shown_in_cfp(event, user):
    """Test that only public tags are available in the CfP form."""
    with scope(event=event):
        public_tag = Tag.objects.create(
            event=event, tag="Public Tag", is_public=True
        )
        private_tag = Tag.objects.create(
            event=event, tag="Private Tag", is_public=False
        )
        event.cfp.fields["tags"]["visibility"] = "optional"
        event.cfp.save()

        form = InfoForm(event=event)
        available_tags = list(form.fields["tags"].queryset)

        assert public_tag in available_tags
        assert private_tag not in available_tags


@pytest.mark.django_db
def test_tags_min_number_validation(event, user, submission):
    """Test that min_number validation works for tags."""
    with scope(event=event):
        tag1 = Tag.objects.create(event=event, tag="Tag 1", is_public=True)
        tag2 = Tag.objects.create(event=event, tag="Tag 2", is_public=True)

        event.cfp.fields["tags"]["visibility"] = "optional"
        event.cfp.fields["tags"]["min_number"] = 2
        event.cfp.fields["tags"]["max_number"] = None
        event.cfp.save()

        submission_type = SubmissionType.objects.filter(event=event).first()

        # Test with fewer tags than minimum (should fail)
        form_data = {
            "title": "Test Submission",
            "content_locale": "en",
            "abstract": "Test abstract",
            "submission_type": submission_type.pk,
            "tags": [tag1.pk],
        }
        form = InfoForm(event=event, data=form_data)
        assert not form.is_valid()
        assert "tags" in form.errors

        # Test with exact minimum (should pass)
        form_data["tags"] = [tag1.pk, tag2.pk]
        form = InfoForm(event=event, data=form_data)
        assert form.is_valid()


@pytest.mark.django_db
def test_tags_max_number_validation(event, user, submission):
    """Test that max_number validation works for tags."""
    with scope(event=event):
        tag1 = Tag.objects.create(event=event, tag="Tag 1", is_public=True)
        tag2 = Tag.objects.create(event=event, tag="Tag 2", is_public=True)
        tag3 = Tag.objects.create(event=event, tag="Tag 3", is_public=True)

        event.cfp.fields["tags"]["visibility"] = "optional"
        event.cfp.fields["tags"]["min_number"] = None
        event.cfp.fields["tags"]["max_number"] = 2
        event.cfp.save()

        submission_type = SubmissionType.objects.filter(event=event).first()

        # Test with more tags than maximum (should fail)
        form_data = {
            "title": "Test Submission",
            "content_locale": "en",
            "abstract": "Test abstract",
            "submission_type": submission_type.pk,
            "tags": [tag1.pk, tag2.pk, tag3.pk],
        }
        form = InfoForm(event=event, data=form_data)
        assert not form.is_valid()
        assert "tags" in form.errors

        # Test with exact maximum (should pass)
        form_data["tags"] = [tag1.pk, tag2.pk]
        form = InfoForm(event=event, data=form_data)
        assert form.is_valid()


@pytest.mark.django_db
def test_tags_min_max_range_validation(event, user, submission):
    """Test that min and max number validation work together."""
    with scope(event=event):
        tag1 = Tag.objects.create(event=event, tag="Tag 1", is_public=True)
        tag2 = Tag.objects.create(event=event, tag="Tag 2", is_public=True)
        tag3 = Tag.objects.create(event=event, tag="Tag 3", is_public=True)

        event.cfp.fields["tags"]["visibility"] = "optional"
        event.cfp.fields["tags"]["min_number"] = 1
        event.cfp.fields["tags"]["max_number"] = 2
        event.cfp.save()

        submission_type = SubmissionType.objects.filter(event=event).first()

        # Test with 0 tags (should fail - below min)
        form_data = {
            "title": "Test Submission",
            "content_locale": "en",
            "abstract": "Test abstract",
            "submission_type": submission_type.pk,
            "tags": [],
        }
        form = InfoForm(event=event, data=form_data)
        assert not form.is_valid()
        assert "tags" in form.errors

        # Test with 1 tag (should pass - within range)
        form_data["tags"] = [tag1.pk]
        form = InfoForm(event=event, data=form_data)
        assert form.is_valid()

        # Test with 2 tags (should pass - at max)
        form_data["tags"] = [tag1.pk, tag2.pk]
        form = InfoForm(event=event, data=form_data)
        assert form.is_valid()

        # Test with 3 tags (should fail - above max)
        form_data["tags"] = [tag1.pk, tag2.pk, tag3.pk]
        form = InfoForm(event=event, data=form_data)
        assert not form.is_valid()
        assert "tags" in form.errors


@pytest.mark.django_db
def test_tags_validation_error_message(event, user, submission):
    """Test that validation error messages are helpful."""
    with scope(event=event):
        tag1 = Tag.objects.create(event=event, tag="Tag 1", is_public=True)

        event.cfp.fields["tags"]["visibility"] = "optional"
        event.cfp.fields["tags"]["min_number"] = 2
        event.cfp.fields["tags"]["max_number"] = 3
        event.cfp.save()

        submission_type = SubmissionType.objects.filter(event=event).first()

        # Test error message
        form_data = {
            "title": "Test Submission",
            "content_locale": "en",
            "abstract": "Test abstract",
            "submission_type": submission_type.pk,
            "tags": [tag1.pk],
        }
        form = InfoForm(event=event, data=form_data)
        assert not form.is_valid()
        assert "tags" in form.errors
        error_message = str(form.errors["tags"][0])
        assert "2" in error_message  # min_number
        assert "3" in error_message  # max_number
        assert "1" in error_message  # selected count


@pytest.mark.django_db
def test_tags_help_text_with_min_max(event, user):
    """Test that help text shows min/max requirements."""
    with scope(event=event):
        Tag.objects.create(event=event, tag="Test Tag", is_public=True)
        event.cfp.fields["tags"]["visibility"] = "optional"
        event.cfp.fields["tags"]["min_number"] = 1
        event.cfp.fields["tags"]["max_number"] = 3
        event.cfp.save()

        form = InfoForm(event=event)
        help_text = form.fields["tags"].help_text

        assert "1" in help_text  # min_number
        assert "3" in help_text  # max_number


@pytest.mark.django_db
def test_tags_no_validation_without_min_max(event, user, submission):
    """Test that no validation is applied when min/max are not set."""
    with scope(event=event):
        tag1 = Tag.objects.create(event=event, tag="Tag 1", is_public=True)
        tag2 = Tag.objects.create(event=event, tag="Tag 2", is_public=True)

        event.cfp.fields["tags"]["visibility"] = "optional"
        event.cfp.fields["tags"]["min_number"] = None
        event.cfp.fields["tags"]["max_number"] = None
        event.cfp.save()

        submission_type = SubmissionType.objects.filter(event=event).first()

        # Test with 0 tags (should pass)
        form_data = {
            "title": "Test Submission",
            "content_locale": "en",
            "abstract": "Test abstract",
            "submission_type": submission_type.pk,
            "tags": [],
        }
        form = InfoForm(event=event, data=form_data)
        assert form.is_valid()

        # Test with many tags (should pass)
        form_data["tags"] = [tag1.pk, tag2.pk]
        form = InfoForm(event=event, data=form_data)
        assert form.is_valid()
