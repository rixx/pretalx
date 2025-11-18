import pytest


@pytest.mark.django_db
def test_speaker_change_request_view_disabled(client, submission):
    submission.event.feature_flags["allow_speaker_change_requests"] = False
    submission.event.save()
    client.force_login(submission.speakers.first())
    response = client.get(submission.urls.request_changes)
    assert response.status_code == 302


@pytest.mark.django_db
def test_speaker_change_request_view_editable(client, submission):
    client.force_login(submission.speakers.first())
    response = client.get(submission.urls.request_changes)
    assert response.status_code == 302


@pytest.mark.django_db
def test_speaker_change_request_view_get(client, submission):
    submission.state = "accepted"
    submission.event.active_review_phase = None
    submission.event.feature_flags["speakers_can_edit_submissions"] = False
    submission.event.save()
    submission.save()
    client.force_login(submission.speakers.first())
    response = client.get(submission.urls.request_changes)
    assert response.status_code == 200


@pytest.mark.django_db
def test_speaker_change_request_submit(client, submission):
    submission.state = "accepted"
    submission.event.active_review_phase = None
    submission.event.feature_flags["speakers_can_edit_submissions"] = False
    submission.event.save()
    submission.save()
    speaker = submission.speakers.first()
    client.force_login(speaker)
    response = client.post(
        submission.urls.request_changes,
        {
            "title": "New Title",
            "abstract": submission.abstract,
            "description": submission.description,
            "submission_type": submission.submission_type.pk,
            "content_locale": submission.content_locale,
            "change_request_comment": "Please update the title",
        },
        follow=True,
    )
    submission.refresh_from_db()
    assert submission.has_change_request
    assert submission.change_request["comment"] == "Please update the title"
    assert "title" in submission.change_request["changes"]


@pytest.mark.django_db
def test_speaker_change_request_no_changes(client, submission):
    submission.state = "accepted"
    submission.event.active_review_phase = None
    submission.event.feature_flags["speakers_can_edit_submissions"] = False
    submission.event.save()
    submission.save()
    client.force_login(submission.speakers.first())
    response = client.post(
        submission.urls.request_changes,
        {
            "title": submission.title,
            "abstract": submission.abstract,
            "description": submission.description,
            "submission_type": submission.submission_type.pk,
            "content_locale": submission.content_locale,
        },
        follow=True,
    )
    submission.refresh_from_db()
    assert not submission.has_change_request
