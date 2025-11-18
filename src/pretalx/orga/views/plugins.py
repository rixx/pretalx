# SPDX-FileCopyrightText: 2018-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import logging

from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django_context_decorator import context

from pretalx.common.plugins import get_all_plugins_grouped
from pretalx.common.text.phrases import phrases
from pretalx.common.views.mixins import EventPermissionRequired

logger = logging.getLogger(__name__)


class EventPluginsView(EventPermissionRequired, TemplateView):
    template_name = "orga/plugins.html"
    permission_required = "event.update_event"

    @context
    @cached_property
    def grouped_plugins(self):
        return get_all_plugins_grouped(self.request.event)

    @context
    def tablist(self):
        return dict(self.grouped_plugins.keys())

    @context
    @cached_property
    def plugins_active(self):
        return self.request.event.plugin_list

    def _prepare_links(self, links):
        """Prepare plugin links for display.

        Args:
            links: List of tuples in format ((label, ...), urlname, url_kwargs)

        Returns:
            List of dicts with 'label' and 'url' keys
        """
        if not links:
            return []

        result = []
        for link_tuple in links:
            try:
                labels, urlname, url_kwargs = link_tuple
            except (TypeError, ValueError) as e:
                logger.warning(
                    "Invalid link tuple format in plugin links: %s",
                    link_tuple,
                    exc_info=True
                )
                continue

            # labels can be a single string or a tuple of strings
            if isinstance(labels, str):
                label = labels
            else:
                # Join multiple labels with " > " separator
                label = " > ".join(str(l) for l in labels)

            # Build the URL with event context
            try:
                kwargs = {"event": self.request.event.slug}
                if url_kwargs:
                    kwargs.update(url_kwargs)
                url = reverse(urlname, kwargs=kwargs)
                result.append({"label": label, "url": url})
            except (NoReverseMatch, ImproperlyConfigured) as e:
                # Skip links that can't be resolved
                logger.debug(
                    "Could not resolve URL '%s' for plugin link: %s",
                    urlname,
                    e
                )

        return result

    @context
    @cached_property
    def plugin_links(self):
        """Prepare settings_links and navigation_links for all active plugins."""
        links = {}
        for category, plugins in self.grouped_plugins.items():
            for plugin in plugins:
                if plugin.module in self.plugins_active:
                    plugin_links = {}
                    if hasattr(plugin, "settings_links"):
                        plugin_links["settings"] = self._prepare_links(plugin.settings_links)
                    if hasattr(plugin, "navigation_links"):
                        plugin_links["navigation"] = self._prepare_links(plugin.navigation_links)

                    if plugin_links:
                        links[plugin.module] = plugin_links

        return links

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            for key, value in request.POST.items():
                if key.startswith("plugin:"):
                    module = key.split(":", maxsplit=1)[1]
                    if (
                        value == "enable"
                        and module in self.request.event.available_plugins
                    ):
                        self.request.event.enable_plugin(module)
                        self.request.event.log_action(
                            "pretalx.event.plugins.enabled",
                            person=self.request.user,
                            # TODO log name and display
                            data={"plugin": module},
                            orga=True,
                        )
                    else:
                        self.request.event.disable_plugin(module)
                        self.request.event.log_action(
                            "pretalx.event.plugins.disabled",
                            person=self.request.user,
                            data={"plugin": module},
                            orga=True,
                        )
            self.request.event.save()
            messages.success(self.request, phrases.base.saved)
        return redirect(self.request.event.orga_urls.plugins)
