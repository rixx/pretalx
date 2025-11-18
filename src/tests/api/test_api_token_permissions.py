# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import json

import pytest
from django_scopes import scope

from pretalx.person.models.auth_token import ENDPOINTS, UserApiToken, generate_api_token


@pytest.mark.django_db
def test_token_with_no_events_grants_access_to_user_events(
    client, event, orga_user
):
    """Test that a token with no events field can access all events the user has permission for."""
    token = UserApiToken.objects.create(name="all-events-token", user=orga_user)
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    assert not token.events.exists()

    response = client.get(
        event.api_urls.submissions,
        follow=True,
        headers={"Authorization": f"Token {token.token}"},
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_token_with_no_events_cannot_access_unauthorized_events(
    client, event, django_user_model
):
    """Test that a token with no events cannot access events the user doesn't have permission for."""
    user = django_user_model.objects.create_user(
        email="unauthorized@example.com", password="testpass", name="Unauthorized User"
    )
    token = UserApiToken.objects.create(name="all-events-token", user=user)
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    assert not token.events.exists()

    response = client.get(
        event.api_urls.submissions,
        follow=True,
        headers={"Authorization": f"Token {token.token}"},
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_token_with_specific_events_only_accesses_those_events(
    client, event, other_event, orga_user
):
    """Test that a token with specific events can only access those events."""
    token = UserApiToken.objects.create(name="specific-event-token", user=orga_user)
    token.events.set([event])
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    assert token.events.count() == 1
    assert event in token.events.all()

    response = client.get(
        event.api_urls.submissions,
        follow=True,
        headers={"Authorization": f"Token {token.token}"},
    )
    assert response.status_code == 200

    response = client.get(
        other_event.api_urls.submissions,
        follow=True,
        headers={"Authorization": f"Token {token.token}"},
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_token_with_no_events_works_across_multiple_user_events(
    client, event, orga_user
):
    """Test that a token with no events can access all events the user has permission for."""
    from django_scopes import scopes_disabled

    from pretalx.event.models import Event

    with scopes_disabled():
        organiser = event.organiser
        other_event = Event.objects.create(
            name="Second Event",
            slug="second",
            organiser=organiser,
            email="orga@orga.org",
            date_from=event.date_from,
            date_to=event.date_to,
        )
        team = organiser.teams.filter(
            can_change_organiser_settings=True, is_reviewer=False
        ).first()
        team.limit_events.add(other_event)

    token = UserApiToken.objects.create(name="all-events-token", user=orga_user)
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    assert not token.events.exists()

    response = client.get(
        event.api_urls.submissions,
        follow=True,
        headers={"Authorization": f"Token {token.token}"},
    )
    assert response.status_code == 200

    response = client.get(
        other_event.api_urls.submissions,
        follow=True,
        headers={"Authorization": f"Token {token.token}"},
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_token_serialize_with_no_events():
    """Test that serializing a token with no events returns None for events field."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(
        email="test@example.com", password="testpass", name="Test User"
    )

    token = UserApiToken.objects.create(name="test-token", user=user)
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    serialized = token.serialize()

    assert serialized["events"] is None
    assert serialized["name"] == "test-token"
    assert serialized["endpoints"] == token.endpoints


@pytest.mark.django_db
def test_token_serialize_with_specific_events(event, orga_user):
    """Test that serializing a token with specific events returns a list of event slugs."""
    token = UserApiToken.objects.create(name="test-token", user=orga_user)
    token.events.set([event])
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    serialized = token.serialize()

    assert serialized["events"] == [event.slug]
    assert serialized["name"] == "test-token"


@pytest.mark.django_db
def test_update_events_preserves_token_with_no_events(orga_user):
    """Test that update_events() doesn't expire tokens with no events."""
    token = UserApiToken.objects.create(name="all-events-token", user=orga_user)
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    assert not token.events.exists()
    assert token.is_active

    token.update_events()

    token.refresh_from_db()
    assert token.is_active
    assert not token.events.exists()


@pytest.mark.django_db
def test_update_events_removes_unauthorized_events(event, other_event, orga_user):
    """Test that update_events() removes events the user no longer has access to."""
    token = UserApiToken.objects.create(name="specific-event-token", user=orga_user)
    token.events.set([event, other_event])
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    assert token.events.count() == 2

    with scope(event=event):
        team = orga_user.teams.first()
        team.limit_events.set([event])

    token.update_events()

    token.refresh_from_db()
    assert token.events.count() == 1
    assert event in token.events.all()
    assert other_event not in token.events.all()
    assert token.is_active


@pytest.mark.django_db
def test_update_events_expires_token_when_all_events_removed(event, orga_user):
    """Test that update_events() expires a token when all events are removed."""
    token = UserApiToken.objects.create(name="specific-event-token", user=orga_user)
    token.events.set([event])
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    assert token.events.count() == 1
    assert token.is_active

    with scope(event=event):
        team = orga_user.teams.first()
        team.members.remove(orga_user)

    token.update_events()

    token.refresh_from_db()
    assert not token.is_active
    assert not token.events.exists()
