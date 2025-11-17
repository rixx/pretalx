# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import pytest

from pretalx import __version__
from pretalx.api.versions import CURRENT_VERSION


@pytest.mark.django_db
def test_metadata_endpoint(client):
    response = client.get("/api/")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == CURRENT_VERSION
    assert data["pretalx_version"] == __version__
    assert "events" in data
    assert data["events"].endswith("/api/events/")


@pytest.mark.django_db
def test_metadata_endpoint_is_public(client):
    """The metadata endpoint should be accessible without authentication."""
    response = client.get("/api/")
    assert response.status_code == 200
