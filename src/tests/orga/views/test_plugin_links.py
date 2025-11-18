# SPDX-FileCopyrightText: 2018-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import pytest
from django.test import RequestFactory
from django.urls import reverse

from pretalx.orga.views.plugins import EventPluginsView


@pytest.mark.django_db
class TestPluginLinksView:
    """Test plugin links functionality in EventPluginsView."""

    def setup_view(self, event, user):
        """Helper to set up a view with a proper request."""
        factory = RequestFactory()
        request = factory.get("/")
        request.event = event
        request.user = user

        view = EventPluginsView()
        view.request = request
        return view

    def test_prepare_links_with_single_label(self, event, orga_user):
        """Test _prepare_links with single string labels."""
        view = self.setup_view(event, orga_user)

        links = [
            (("Settings",), "orga:settings.plugins.select", {}),
        ]
        result = view._prepare_links(links)

        assert len(result) == 1
        assert result[0]["label"] == "Settings"
        assert result[0]["url"] == reverse("orga:settings.plugins.select", kwargs={"event": event.slug})

    def test_prepare_links_with_multiple_labels(self, event, orga_user):
        """Test _prepare_links with multiple labels (breadcrumb style)."""
        view = self.setup_view(event, orga_user)

        links = [
            (("Plugin", "Settings"), "orga:settings.plugins.select", {}),
        ]
        result = view._prepare_links(links)

        assert len(result) == 1
        assert result[0]["label"] == "Plugin > Settings"

    def test_prepare_links_with_url_kwargs(self, event, orga_user, submission):
        """Test _prepare_links with additional URL kwargs."""
        view = self.setup_view(event, orga_user)

        links = [
            (("View Submission",), "orga:submissions.content.view", {"code": submission.code}),
        ]
        result = view._prepare_links(links)

        assert len(result) == 1
        assert result[0]["url"] == reverse(
            "orga:submissions.content.view",
            kwargs={"event": event.slug, "code": submission.code}
        )

    def test_prepare_links_with_empty_list(self, event, orga_user):
        """Test _prepare_links with empty list."""
        view = self.setup_view(event, orga_user)

        result = view._prepare_links([])
        assert result == []

    def test_prepare_links_with_none(self, event, orga_user):
        """Test _prepare_links with None."""
        view = self.setup_view(event, orga_user)

        result = view._prepare_links(None)
        assert result == []

    def test_prepare_links_with_invalid_url(self, event, orga_user):
        """Test _prepare_links skips invalid URLs."""
        view = self.setup_view(event, orga_user)

        links = [
            (("Valid",), "orga:settings.plugins.select", {}),
            (("Invalid",), "nonexistent:url", {}),
            (("Also Valid",), "orga:settings.plugins.select", {}),
        ]
        result = view._prepare_links(links)

        # Should only have 2 valid links
        assert len(result) == 2
        assert result[0]["label"] == "Valid"
        assert result[1]["label"] == "Also Valid"

    def test_prepare_links_with_invalid_tuple_format(self, event, orga_user):
        """Test _prepare_links handles malformed tuples."""
        view = self.setup_view(event, orga_user)

        links = [
            (("Valid",), "orga:settings.plugins.select", {}),
            ("not a valid tuple",),  # Invalid format
            (("Also Valid",), "orga:settings.plugins.select", {}),
        ]
        result = view._prepare_links(links)

        # Should skip the invalid one
        assert len(result) == 2
        assert result[0]["label"] == "Valid"
        assert result[1]["label"] == "Also Valid"

    def test_prepare_links_with_string_label(self, event, orga_user):
        """Test _prepare_links with string (not tuple) as first element."""
        view = self.setup_view(event, orga_user)

        links = [
            ("Simple Label", "orga:settings.plugins.select", {}),
        ]
        result = view._prepare_links(links)

        assert len(result) == 1
        assert result[0]["label"] == "Simple Label"


@pytest.mark.django_db
def test_plugin_links_context_with_active_plugin(event, orga_client, orga_user):
    """Test that plugin_links context includes links for active plugins."""
    event.enable_plugin("tests")
    event.save()

    response = orga_client.get(event.orga_urls.plugins)
    assert response.status_code == 200

    plugin_links = response.context["plugin_links"]
    assert "tests" in plugin_links
    assert "settings" in plugin_links["tests"]
    assert "navigation" in plugin_links["tests"]

    # Check settings links
    settings_links = plugin_links["tests"]["settings"]
    assert len(settings_links) == 1
    assert settings_links[0]["label"] == "Test Settings"

    # Check navigation links
    nav_links = plugin_links["tests"]["navigation"]
    assert len(nav_links) == 1
    assert nav_links[0]["label"] == "Test > Navigation"


@pytest.mark.django_db
def test_plugin_links_context_without_active_plugin(event, orga_client):
    """Test that plugin_links context doesn't include inactive plugins."""
    response = orga_client.get(event.orga_urls.plugins)
    assert response.status_code == 200

    plugin_links = response.context["plugin_links"]
    # Test plugin should not be in plugin_links if not active
    assert "tests" not in plugin_links


@pytest.mark.django_db
def test_plugin_links_template_rendering(event, orga_client):
    """Test that plugin links render correctly in template."""
    event.enable_plugin("tests")
    event.save()

    response = orga_client.get(event.orga_urls.plugins)
    assert response.status_code == 200

    content = response.content.decode()
    # Check for "Go to" button
    assert 'translate "Go to"' in content or "Go to" in content
    # Check for "Settings" button
    assert 'translate "Settings"' in content or "Settings" in content
