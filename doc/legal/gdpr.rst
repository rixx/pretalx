.. SPDX-FileCopyrightText: 2025-present Tobias Kunze
.. SPDX-License-Identifier: CC-BY-SA-4.0

GDPR compliance
===============

.. warning::

    The pretalx documentation is not legal advice.
    Please consult a lawyer specialized in privacy law for binding legal advice.

Data processing
---------------

When using pretalx.com (our hosted service), you act as the data controller and we act as the data processor (Art. 28 GDPR).

We strongly recommend that you sign a Data Protection Agreement (DPA) with us to be in compliance with Art. 28 GDPR.
You can request a DPA through your pretalx.com account.

Unfortunately, we are usually not able to accommodate requests for a customized DPA based on a customer's DPA template.
This is because we act as a processor for a large number of controllers and can only efficiently ensure enforcement of the DPA if the same rules apply across our customer base.

Processing location
-------------------

When using pretalx.com, we only process data within the European Union.
Your data is stored in data centers within Germany.

Records of processing activities
---------------------------------

When describing pretalx in your internal record of processing activities (Art. 30 GDPR), we recommend that you describe why you use pretalx, what data you configure pretalx to collect, and who will receive that data.

We cannot provide you with a template for that description because pretalx is used for a large number of purposes.
Depending on your specific use case, the categories of data subjects and the categories of personal data might be completely different to those of another user of pretalx.

For example, a conference using pretalx typically processes:

- Personal data of **speakers** (name, email, biographical information, profile pictures)
- Personal data of **reviewers** (name, email, review activity)
- Personal data of **organizers** (name, email, administrative actions)
- Personal data of **attendees** who interact with the public schedule (optional, depending on features used)

The specific data collected depends heavily on your configuration and the questions you ask during the call for participation.

Data protection by design and by default
-----------------------------------------

pretalx is designed to minimize risk by collecting only very minimal data in its default configuration (Art. 25 GDPR).

Specifically, in its most basic configuration for a call for participation, pretalx will collect:

- Speaker name and email address
- Submission title and abstract
- Any additional information you configure through custom questions

Every additional data collection feature can be turned off and is either disabled or optional by default.
It is your obligation to only collect additional personal data that you require to run your event.

pretalx does **not** process payment data, as it is not a ticketing system.

Security of processing
----------------------

pretalx applies state-of-the-art security mechanisms (Art. 32 GDPR).
The application supports modern cryptography and authentication schemes.

For pretalx.com (our hosted service), we take care of automated monitoring, security updates, and backups.
You can learn more on our website: `Security at pretalx <https://pretalx.com/p/about>`_.

Rights of the data subject
---------------------------

pretalx includes tools to allow you to help your users with exercising their rights.

Transparent information (Art. 12-13 GDPR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should include a link to your privacy policy in your event's pages.
We recommend adding this to your call for participation form and your event's footer.

Right of access (Art. 15 GDPR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users can access their own data by logging into their pretalx account.
All submission data, profile information, and activity associated with their account is accessible through the user interface.

For data subject access requests, event organizers can export relevant data through the organizer interface or by directly accessing the database records for self-hosted installations.

Right to rectification, erasure, and restriction (Art. 16-18 GDPR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users can modify their own profile data and submission data at any time through the pretalx interface (subject to submission deadlines you configure).

As event organizers, you can modify or delete data through the organizer interface.
However, please note that some data may need to be retained for legitimate purposes such as:

- Maintaining the integrity of the review process
- Providing a historical record of your event's program
- Complying with legal retention requirements

pretalx provides tools to anonymize or delete personal data after an event is completed, if you no longer have a legal basis for retaining it.

Automated decision-making (Art. 22 GDPR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In our opinion, pretalx does not include any functionality that falls under the provisions of Art. 22 GDPR.
All decisions about accepting or rejecting submissions are made by human reviewers and organizers.
