# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import pytest

from pretalx.person.models.auth_token import (
    ENDPOINTS,
    READ_PERMISSIONS,
    WRITE_PERMISSIONS,
    UserApiToken,
    generate_api_token,
)


@pytest.mark.django_db
def test_token_get_permission_preset_read(orga_user):
    """Test that a token with read permissions on all endpoints is detected as 'read' preset."""
    token = UserApiToken.objects.create(name="test_read", user=orga_user)
    token.endpoints = {endpoint: list(READ_PERMISSIONS) for endpoint in ENDPOINTS}
    token.save()

    assert token.get_permission_preset() == "read"


@pytest.mark.django_db
def test_token_get_permission_preset_write(orga_user):
    """Test that a token with write permissions on all endpoints is detected as 'write' preset."""
    token = UserApiToken.objects.create(name="test_write", user=orga_user)
    token.endpoints = {endpoint: list(WRITE_PERMISSIONS) for endpoint in ENDPOINTS}
    token.save()

    assert token.get_permission_preset() == "write"


@pytest.mark.django_db
def test_token_get_permission_preset_custom_partial_endpoints(orga_user):
    """Test that a token with only some endpoints configured is detected as 'custom'."""
    token = UserApiToken.objects.create(name="test_custom", user=orga_user)
    token.endpoints = {"events": list(READ_PERMISSIONS), "submissions": list(READ_PERMISSIONS)}
    token.save()

    assert token.get_permission_preset() == "custom"


@pytest.mark.django_db
def test_token_get_permission_preset_custom_mixed_permissions(orga_user):
    """Test that a token with different permissions on different endpoints is detected as 'custom'."""
    token = UserApiToken.objects.create(name="test_custom", user=orga_user)
    token.endpoints = {
        endpoint: (list(READ_PERMISSIONS) if i % 2 == 0 else list(WRITE_PERMISSIONS))
        for i, endpoint in enumerate(ENDPOINTS)
    }
    token.save()

    assert token.get_permission_preset() == "custom"


@pytest.mark.django_db
def test_token_get_permission_preset_custom_unusual_permissions(orga_user):
    """Test that a token with non-standard permission combinations is detected as 'custom'."""
    token = UserApiToken.objects.create(name="test_custom", user=orga_user)
    token.endpoints = {endpoint: ["list", "create"] for endpoint in ENDPOINTS}
    token.save()

    assert token.get_permission_preset() == "custom"


@pytest.mark.django_db
def test_token_get_permission_preset_empty(orga_user):
    """Test that a token with no endpoints is detected as 'custom'."""
    token = UserApiToken.objects.create(name="test_empty", user=orga_user)
    token.endpoints = {}
    token.save()

    assert token.get_permission_preset() == "custom"


@pytest.mark.django_db
def test_token_get_capabilities_display_read(orga_user):
    """Test capabilities display for read preset."""
    token = UserApiToken.objects.create(name="test_read", user=orga_user)
    token.endpoints = {endpoint: list(READ_PERMISSIONS) for endpoint in ENDPOINTS}
    token.save()

    display = token.get_capabilities_display()
    assert display["preset"] == "read"
    assert "custom_permissions" not in display


@pytest.mark.django_db
def test_token_get_capabilities_display_write(orga_user):
    """Test capabilities display for write preset."""
    token = UserApiToken.objects.create(name="test_write", user=orga_user)
    token.endpoints = {endpoint: list(WRITE_PERMISSIONS) for endpoint in ENDPOINTS}
    token.save()

    display = token.get_capabilities_display()
    assert display["preset"] == "write"
    assert "custom_permissions" not in display


@pytest.mark.django_db
def test_token_get_capabilities_display_custom(orga_user):
    """Test capabilities display for custom permissions."""
    token = UserApiToken.objects.create(name="test_custom", user=orga_user)
    custom_endpoints = {
        "events": ["list", "retrieve"],
        "submissions": ["list", "retrieve", "create", "update"],
    }
    token.endpoints = custom_endpoints
    token.save()

    display = token.get_capabilities_display()
    assert display["preset"] == "custom"
    assert "custom_permissions" in display
    assert display["custom_permissions"] == custom_endpoints


@pytest.mark.django_db
def test_existing_read_token_fixture(orga_user):
    """Test that a token created like the orga_user_token fixture is correctly detected as read."""
    token = UserApiToken.objects.create(name="testtoken", user=orga_user)
    token.endpoints = {key: ["list", "retrieve"] for key in ENDPOINTS}
    token.save()

    assert token.get_permission_preset() == "read"


@pytest.mark.django_db
def test_existing_write_token_fixture(orga_user):
    """Test that a token created like the write token fixture is correctly detected as write."""
    token = UserApiToken.objects.create(name="testtoken", user=orga_user)
    token.endpoints = {
        key: ["list", "retrieve", "create", "update", "destroy", "actions"]
        for key in ENDPOINTS
    }
    token.save()

    assert token.get_permission_preset() == "write"
