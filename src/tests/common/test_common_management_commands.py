# SPDX-FileCopyrightText: 2018-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import datetime as dt
import os
import subprocess
from contextlib import suppress

import pytest
import responses
from django.core.management import call_command
from django_scopes import scope

from pretalx.event.models import Event


@pytest.mark.django_db
@responses.activate
def test_common_runperiodic():
    responses.add(
        responses.POST,
        "https://pretalx.com/.update_check/",
        json="{}",
        status=404,
        content_type="application/json",
    )
    call_command("runperiodic")


@pytest.mark.skipif(
    "CI" not in os.environ or not os.environ["CI"],
    reason="Having Faker installed increases test runtime, so we just test this on CI.",
)
@pytest.mark.parametrize("stage", ("cfp", "review", "over", "schedule"))
@pytest.mark.django_db
def test_common_test_event(administrator, stage):
    call_command("create_test_event", stage=stage)
    assert Event.objects.get(slug="democon")


@pytest.mark.skipif(
    "CI" not in os.environ or not os.environ["CI"],
    reason="Having Faker installed increases test runtime, so we just test this on CI.",
)
@pytest.mark.django_db
def test_common_test_event_with_seed(administrator):
    call_command("create_test_event", seed=1)
    assert Event.objects.get(slug="democon")


@pytest.mark.skipif(
    "CI" not in os.environ or not os.environ["CI"],
    reason="Having Faker installed increases test runtime, so we just test this on CI.",
)
@pytest.mark.django_db
def test_common_test_event_without_user():
    call_command("create_test_event")
    assert Event.objects.count() == 0


@pytest.mark.django_db
def test_common_uncallable(event):
    with pytest.raises(OSError):
        call_command("init")
    with pytest.raises(Exception):  # noqa
        call_command("shell", "--unsafe-disable-scopes")


@pytest.mark.django_db
def test_common_custom_migrate_does_not_blow_up():
    call_command("migrate")


@pytest.mark.django_db
def test_common_custom_makemessages_does_not_blow_up():
    call_command("makemessages", "--keep-pot", locale=["de_DE"])
    with suppress(Exception):
        subprocess.run(
            [
                "git",
                "checkout",
                "--",
                "pretalx/locale/de_DE",
                "pretalx/locale/django.pot",
            ]
        )


@pytest.mark.django_db
def test_common_move_event(event, slot):
    with scope(event=event):
        old_start = event.date_from
        first_start = slot.start
    call_command(
        "move_event",
        event=event.slug,
        date=(event.date_from + dt.timedelta(days=1)).strftime("%Y-%m-%d"),
    )
    with scope(event=event):
        event.refresh_from_db()
        new_start = event.date_from
        assert new_start != old_start
        slot.refresh_from_db()
        assert slot.start != first_start
    call_command("move_event", event=event.slug)
    with scope(event=event):
        event.refresh_from_db()
        assert event.date_from == old_start


@pytest.mark.django_db
def test_generate_api_docs():
    # Just make sure there is no exception
    call_command("spectacular")


@pytest.mark.django_db
def test_archive_activity_logs_dry_run(event, submission, orga_user):
    """Test dry run mode doesn't delete logs."""
    from django_scopes import scopes_disabled
    from pretalx.common.models import ActivityLog
    
    with scope(event=event):
        # Create some old logs
        old_log = submission.log_action(
            "pretalx.submission.create",
            person=orga_user,
            orga=True,
            data={"title": submission.title},
        )
        # Manually set timestamp to be old
        old_log.timestamp = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        old_log.save()
    
    with scopes_disabled():
        initial_count = ActivityLog.objects.count()
    
    # Run command in dry-run mode
    call_command("archive_activity_logs", "--older-than-days=365", "--dry-run", "--yes")
    
    # Count should be unchanged
    with scopes_disabled():
        assert ActivityLog.objects.count() == initial_count


@pytest.mark.django_db
def test_archive_activity_logs_deletes_old_logs(event, submission, orga_user):
    """Test that old logs are deleted."""
    from django_scopes import scopes_disabled
    from pretalx.common.models import ActivityLog
    
    with scope(event=event):
        # Create an old log
        old_log = submission.log_action(
            "pretalx.submission.create",
            person=orga_user,
            orga=True,
            data={"title": submission.title},
        )
        old_log_id = old_log.id
        old_log.timestamp = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        old_log.save()
        
        # Create a recent log
        recent_log = submission.log_action(
            "pretalx.submission.update",
            person=orga_user,
            orga=True,
            data={"title": "Updated"},
        )
        recent_log_id = recent_log.id
    
    # Run command
    call_command("archive_activity_logs", "--older-than-days=365", "--yes")
    
    # Old log should be deleted, recent log should remain
    with scopes_disabled():
        assert not ActivityLog.objects.filter(id=old_log_id).exists()
        assert ActivityLog.objects.filter(id=recent_log_id).exists()


@pytest.mark.django_db
def test_archive_activity_logs_event_filter(event, other_event, submission, orga_user):
    """Test filtering by event slug."""
    from django_scopes import scopes_disabled
    from pretalx.common.models import ActivityLog
    
    with scope(event=event):
        # Create old log for main event
        event_log = submission.log_action(
            "pretalx.submission.create",
            person=orga_user,
            orga=True,
            data={"title": submission.title},
        )
        event_log.timestamp = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        event_log.save()
        event_log_id = event_log.id
    
    with scope(event=other_event):
        # Create old log for other event
        other_log = other_event.log_action(
            "pretalx.event.update",
            person=orga_user,
            orga=True,
            data={"name": "Test"},
        )
        other_log.timestamp = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        other_log.save()
        other_log_id = other_log.id
    
    # Run command with event filter
    call_command(
        "archive_activity_logs",
        "--older-than-days=365",
        f"--event={event.slug}",
        "--yes"
    )
    
    # Only main event log should be deleted
    with scopes_disabled():
        assert not ActivityLog.objects.filter(id=event_log_id).exists()
        assert ActivityLog.objects.filter(id=other_log_id).exists()


@pytest.mark.django_db
def test_archive_activity_logs_minimum_age_safety(event, submission, orga_user):
    """Test that logs less than 90 days old cannot be deleted."""
    from django.core.management import CommandError
    
    with scope(event=event):
        submission.log_action(
            "pretalx.submission.create",
            person=orga_user,
            orga=True,
            data={"title": submission.title},
        )
    
    # Should raise error for less than 90 days
    with pytest.raises(CommandError, match="Cannot delete logs less than 90 days old"):
        call_command("archive_activity_logs", "--older-than-days=30", "--yes")


@pytest.mark.django_db
def test_archive_activity_logs_with_archival(event, submission, orga_user, tmp_path):
    """Test archiving logs to file before deletion."""
    import gzip
    import json
    from django_scopes import scopes_disabled
    from pretalx.common.models import ActivityLog
    
    with scope(event=event):
        # Create an old log
        old_log = submission.log_action(
            "pretalx.submission.create",
            person=orga_user,
            orga=True,
            data={"title": submission.title},
        )
        old_log.timestamp = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        old_log.save()
        old_log_id = old_log.id
    
    # Run command with archive path
    archive_dir = tmp_path / "archives"
    call_command(
        "archive_activity_logs",
        "--older-than-days=365",
        f"--archive-to={archive_dir}",
        "--yes"
    )
    
    # Log should be deleted
    with scopes_disabled():
        assert not ActivityLog.objects.filter(id=old_log_id).exists()
    
    # Archive file should exist
    archive_files = list(archive_dir.glob("*.jsonl.gz"))
    assert len(archive_files) == 1
    
    # Verify archive content
    with gzip.open(archive_files[0], "rt", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1
        archived_log = json.loads(lines[0])
        assert archived_log["id"] == old_log_id
        assert archived_log["action_type"] == "pretalx.submission.create"
    
    # Metadata file should exist
    metadata_files = list(archive_dir.glob("*.json"))
    assert len(metadata_files) == 1
    with open(metadata_files[0]) as f:
        metadata = json.load(f)
        assert metadata["total_logs"] == 1
        assert metadata["event_slug"] is None
