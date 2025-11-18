# SPDX-FileCopyrightText: 2017-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

"""
Name parts handling for structured name storage.

This module provides support for different cultural naming conventions,
allowing events to configure how speaker names are collected and displayed.
"""

from django.utils.translation import gettext_lazy as _

# Name schemes define how names are structured and concatenated
# Each scheme has:
# - fields: list of (field_name, label, size_weight) tuples
# - concatenation: function to build full name from parts
PERSON_NAME_SCHEMES = {
    "given_family": {
        "fields": [
            ("given_name", _("Given name"), 1),
            ("family_name", _("Family name"), 1),
        ],
        "concatenation": lambda d: f"{d.get('given_name', '')} {d.get('family_name', '')}".strip(),
    },
    "family_given": {
        "fields": [
            ("family_name", _("Family name"), 1),
            ("given_name", _("Given name"), 1),
        ],
        "concatenation": lambda d: f"{d.get('family_name', '')} {d.get('given_name', '')}".strip(),
    },
    "full": {
        "fields": [
            ("full_name", _("Full name"), 1),
        ],
        "concatenation": lambda d: d.get("full_name", ""),
    },
    "title_given_family": {
        "fields": [
            ("title", _("Title"), 1),
            ("given_name", _("Given name"), 2),
            ("family_name", _("Family name"), 2),
        ],
        "concatenation": lambda d: " ".join(
            filter(None, [d.get("title", ""), d.get("given_name", ""), d.get("family_name", "")])
        ),
    },
    "given_middle_family": {
        "fields": [
            ("given_name", _("Given name"), 2),
            ("middle_name", _("Middle name"), 1),
            ("family_name", _("Family name"), 2),
        ],
        "concatenation": lambda d: " ".join(
            filter(None, [d.get("given_name", ""), d.get("middle_name", ""), d.get("family_name", "")])
        ),
    },
    "family_nospace_given": {
        "fields": [
            ("family_name", _("Family name"), 1),
            ("given_name", _("Given name"), 1),
        ],
        "concatenation": lambda d: f"{d.get('family_name', '')}{d.get('given_name', '')}".strip(),
    },
}

# Fields that are required when present in a scheme
REQUIRED_NAME_PARTS = ["given_name", "family_name", "full_name"]


def build_name(parts, fallback_scheme="given_family"):
    """
    Build a full name string from structured name parts.

    :param parts: Dictionary containing name components and optionally "_scheme"
    :param fallback_scheme: Scheme to use if not specified in parts
    :return: Concatenated name string
    """
    if not parts:
        return ""

    # Handle legacy names (migrated from simple string field)
    if "_legacy" in parts:
        return parts["_legacy"]

    # Determine which scheme to use
    scheme_name = parts.get("_scheme", fallback_scheme)
    scheme = PERSON_NAME_SCHEMES.get(scheme_name)

    if not scheme:
        scheme = PERSON_NAME_SCHEMES["given_family"]

    return scheme["concatenation"](parts).strip()


def get_name_parts_label(scheme_name, field_name):
    """
    Get the label for a specific name field in a scheme.

    :param scheme_name: Name of the scheme
    :param field_name: Name of the field
    :return: Translated label string
    """
    scheme = PERSON_NAME_SCHEMES.get(scheme_name, PERSON_NAME_SCHEMES["given_family"])
    for fname, label, _ in scheme["fields"]:
        if fname == field_name:
            return label
    return field_name


def name_parts_to_dict(name_string, scheme_name="full"):
    """
    Convert a simple name string to a name_parts dictionary.

    This is useful for migrating existing data or handling legacy input.

    :param name_string: Simple name string
    :param scheme_name: Scheme to use (default "full" for single-field storage)
    :return: Dictionary suitable for name_parts field
    """
    if not name_string:
        return {}

    return {"_legacy": name_string}
