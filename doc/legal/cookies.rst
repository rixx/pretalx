.. SPDX-FileCopyrightText: 2025-present Tobias Kunze
.. SPDX-License-Identifier: CC-BY-SA-4.0

Cookie usage
============

Main application
----------------

If you use pretalx with the default configuration, it will issue the following cookies to clients interacting with it:

.. list-table::
   :header-rows: 1
   :widths: 20 20 15 45

   * - Name
     - Content
     - Lifetime
     - Reason
   * - ``pretalx_csrftoken``
     - Random ID
     - 365 days
     - Security token for form submissions. Provides a security measure against `CSRF attacks <https://en.wikipedia.org/wiki/Cross-site_request_forgery>`_.

       We consider the cookie to be technically necessary to provide the desired functionality. Therefore, it does not require consent.

       We do not correlate this ID with other data sources and do not use it for tracking.
   * - ``pretalx_session``
     - Session ID
     - 14 days
     - This cookie is used to recognize the user session across page loads for all features that require this, such as maintaining a logged-in state for speakers, reviewers, and organizers.

       The cookie will only be set when the user logs in or uses a feature that requires session management.

       We consider the cookie to be technically necessary to provide the desired functionality. Therefore, it does not require consent.

       This cookie is not used for any tracking purposes in the default configuration.
   * - ``pretalx_language``
     - Language ID, such as "en" or "de"
     - 10 years
     - Storage of the user's selected language to display pretalx in the preferred language across sessions.

       Will only be set if the user explicitly changes the language.

       We consider the cookie to be technically necessary to provide the desired functionality. Therefore, it does not require consent.

       Using this cookie for tracking is practically impossible due to the low information content.

Additional cookies may occur due to the usage of plugins.

Schedule widget
---------------

When **loading** the pretalx schedule widget on a page, pretalx **does not** set any cookies in the user's browser.

Even after the user interacts with the widget (e.g., filtering talks, viewing speaker details), **no cookies are set**.
The widget uses only browser local storage to maintain state, such as selected filters or expanded talk details.

Since local storage is never transmitted to our servers and only managed within the browser, this does not constitute tracking and does not require consent.

Cookie consent management
-------------------------

We consider all cookies listed above to be technically necessary to provide the desired functionality.
Therefore, they do not require consent under the `EU ePrivacy Directive <https://en.wikipedia.org/wiki/EPrivacy_Directive>`_.

pretalx does not include cookie consent management functionality because, in its default configuration, it only sets technically necessary cookies.

If you install plugins that set non-necessary cookies (e.g., analytics or tracking scripts), you are responsible for implementing appropriate consent mechanisms and complying with applicable privacy regulations.
