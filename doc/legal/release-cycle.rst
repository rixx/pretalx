.. SPDX-FileCopyrightText: 2025-present Tobias Kunze
.. SPDX-License-Identifier: CC-BY-SA-4.0

Release cycle
=============

Versioning scheme
-----------------

pretalx uses `calendar versioning <https://calver.org/>`_ (CalVer) with a version number scheme of ``YEAR.MINOR.PATCH``.
For example, version ``2025.1.0`` is the first feature release of 2025, and ``2025.1.1`` is the first patch release for that feature release.

Feature releases
-----------------

We publish **2-3 feature releases per year**.
These releases may contain new functionality, removal of deprecated functionality, bug fixes, or any other kind of change.

Feature releases are numbered with a ``.0`` patch version (e.g. ``2025.1.0``, ``2025.2.0``).
We recommend studying the release notes before upgrading if you are concerned about API or plugin compatibility.

All new releases are announced on `our blog <https://pretalx.com/p/news>`_.

Patch releases
--------------

Patch releases have a version number of ``YEAR.MINOR.PATCH`` (e.g. ``2025.1.1`` is the first patch release after ``2025.1.0``).

These releases are not published on a regular schedule, but when required to fix critical issues that cannot wait for the next feature release.
Patch releases typically contain only bug fixes and security fixes, not new features.

We only provide patch releases for the **current feature release**.
For example, if the latest release is ``2025.2.0`` and a critical bug is discovered, we will publish ``2025.2.1``.
We will not publish a patch release for ``2025.1.0`` at that time.

This means you should plan to upgrade to new feature releases to continue receiving bug fixes and security updates.

Plugins
-------

Plugins that are developed and maintained by the pretalx project are released **in sync with pretalx feature releases**.

When we publish a new feature release of pretalx, we also publish updates to our official plugins if there have been changes.
Plugin updates are announced in the same blog post as the pretalx feature release.

We ensure that the latest published versions of our plugins are always compatible with the latest feature release of pretalx.
We therefore recommend updating both plugins and the core system together when upgrading.

Third-party plugins may follow their own release cycles.
