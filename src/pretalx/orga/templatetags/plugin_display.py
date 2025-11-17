# SPDX-FileCopyrightText: 2018-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from django import template

register = template.Library()


@register.filter
def get_dict(dictionary, key):
    """Get a value from a dictionary by key."""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
