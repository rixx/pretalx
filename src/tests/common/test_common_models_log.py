# SPDX-FileCopyrightText: 2022-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import pytest
from django_scopes import scope


@pytest.mark.django_db
def test_log_hides_password(submission):
    with scope(event=submission.event):
        submission.log_action(
            "test.hide", data={"password": "12345", "non-sensitive": "foo"}
        )
        log = submission.logged_actions().get(action_type="test.hide")
        assert log.json_data["password"] != "12345"
        assert log.json_data["non-sensitive"] == "foo"


@pytest.mark.django_db
def test_log_wrong_data(submission):
    with scope(event=submission.event), pytest.raises(TypeError):
        submission.log_action(
            "test.hide", data=[{"password": "12345", "non-sensitive": "foo"}]
        )


@pytest.mark.django_db
def test_get_instance_data(submission):
    """Test that _get_instance_data properly extracts field values."""
    with scope(event=submission.event):
        data = submission._get_instance_data()

        # Check that basic fields are included
        assert "title" in data
        assert data["title"] == submission.title
        assert "state" in data
        assert data["state"] == submission.state

        # Check that ForeignKey is stored as ID
        assert "submission_type" in data
        assert data["submission_type"] == submission.submission_type.pk

        # Check that auto-updated fields are excluded
        assert "created" not in data
        assert "updated" not in data


@pytest.mark.django_db
def test_compute_changes(submission):
    """Test that _compute_changes properly detects field differences."""
    old_data = {"title": "Old Title", "state": "submitted", "track": None}
    new_data = {"title": "New Title", "state": "submitted", "track": 1}

    changes = submission._compute_changes(old_data, new_data)

    # Title changed
    assert "title" in changes
    assert changes["title"]["old"] == "Old Title"
    assert changes["title"]["new"] == "New Title"

    # State didn't change - should not be in changes
    assert "state" not in changes

    # Track changed from None to 1
    assert "track" in changes
    assert changes["track"]["old"] is None
    assert changes["track"]["new"] == 1


@pytest.mark.django_db
def test_compute_changes_no_changes(submission):
    """Test that _compute_changes returns empty dict when nothing changed."""
    data = {"title": "Same Title", "state": "submitted"}
    changes = submission._compute_changes(data, data)
    assert changes == {}


@pytest.mark.django_db
def test_log_action_with_changes(submission):
    """Test that log_action properly stores changes when old_data/new_data provided."""
    with scope(event=submission.event):
        old_data = {"title": "Old Title", "state": "submitted"}
        new_data = {"title": "New Title", "state": "submitted"}

        submission.log_action(
            "test.update",
            old_data=old_data,
            new_data=new_data
        )

        log = submission.logged_actions().get(action_type="test.update")
        assert "changes" in log.json_data
        assert "title" in log.json_data["changes"]
        assert log.json_data["changes"]["title"]["old"] == "Old Title"
        assert log.json_data["changes"]["title"]["new"] == "New Title"
        # State didn't change, should not be in changes
        assert "state" not in log.json_data["changes"]


@pytest.mark.django_db
def test_log_action_no_changes_skips_log(submission):
    """Test that log_action doesn't create entry when no changes detected."""
    with scope(event=submission.event):
        initial_count = submission.logged_actions().count()

        data = {"title": "Same Title", "state": "submitted"}
        submission.log_action(
            "test.update",
            old_data=data,
            new_data=data
        )

        # No new log should be created
        assert submission.logged_actions().count() == initial_count


@pytest.mark.django_db
def test_log_action_no_changes_with_explicit_data_still_logs(submission):
    """Test that log_action creates entry if explicit data provided even with no changes."""
    with scope(event=submission.event):
        data = {"title": "Same Title", "state": "submitted"}
        submission.log_action(
            "test.update",
            data={"custom": "info"},
            old_data=data,
            new_data=data
        )

        log = submission.logged_actions().get(action_type="test.update")
        assert log.json_data["custom"] == "info"
        # No changes key since nothing changed
        assert "changes" not in log.json_data


@pytest.mark.django_db
def test_log_action_changes_with_additional_data(submission):
    """Test that changes are merged with explicit data dict."""
    with scope(event=submission.event):
        old_data = {"title": "Old Title"}
        new_data = {"title": "New Title"}

        submission.log_action(
            "test.update",
            data={"reason": "user requested"},
            old_data=old_data,
            new_data=new_data
        )

        log = submission.logged_actions().get(action_type="test.update")
        # Both changes and custom data should be present
        assert "changes" in log.json_data
        assert "reason" in log.json_data
        assert log.json_data["reason"] == "user requested"
        assert log.json_data["changes"]["title"]["old"] == "Old Title"


@pytest.mark.django_db
def test_log_action_change_tracking_integration(submission):
    """Test end-to-end change tracking with real model update."""
    with scope(event=submission.event):
        # Capture old state
        old_data = submission._get_instance_data()
        old_title = submission.title

        # Update the submission
        submission.title = "Updated Title"
        submission.save()

        # Capture new state
        new_data = submission._get_instance_data()

        # Log the change
        submission.log_action(
            "test.update",
            old_data=old_data,
            new_data=new_data
        )

        log = submission.logged_actions().get(action_type="test.update")
        assert "changes" in log.json_data
        assert "title" in log.json_data["changes"]
        assert log.json_data["changes"]["title"]["old"] == old_title
        assert log.json_data["changes"]["title"]["new"] == "Updated Title"
