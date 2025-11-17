.. SPDX-FileCopyrightText: 2025-present Tobias Kunze
.. SPDX-License-Identifier: CC-BY-SA-4.0

.. _`user-guide-emails`:

Email Communication
===================

pretalx helps you communicate with speakers, reviewers, and other participants
throughout your event. The email system is designed around a key principle:
**nearly every email requires your explicit approval before being sent**. This
gives you control over what speakers receive and when they receive it.

.. important::
    Most emails in pretalx are not sent immediately. Instead, they are placed in
    your **Drafts** folder where you can review, edit, or discard them before
    sending. This prevents accidental communication and gives you time to refine
    your messages.

Understanding Email Drafts
---------------------------

The drafts folder is the heart of pretalx's email system. It's where automatically
generated emails wait for your approval, and where you can compose emails manually.

What Are Email Drafts?
^^^^^^^^^^^^^^^^^^^^^^^

When pretalx needs to send an email – for example, when you accept a proposal or
release a schedule – it doesn't send the email immediately. Instead, it:

1. Generates the email content using your configured template
2. Places the email in your **Drafts** folder at **Mail → Drafts**
3. Waits for you to review and explicitly send it

This means you always have the opportunity to:

- **Review** the email content before it goes out
- **Edit** the text, subject, or recipients
- **Preview** how the email will look to recipients
- **Delete** emails you don't want to send
- **Send** emails when you're ready, either individually or in batches

Accessing Your Drafts
^^^^^^^^^^^^^^^^^^^^^^

Navigate to **Mail → Drafts** in the organiser interface. You'll see a list of
all unsent emails, showing:

- The recipient(s)
- The subject line
- Which template generated the email (if any)
- When the email was created

You can filter drafts by recipient, subject, or track to find specific emails.

Draft Email Workflow
^^^^^^^^^^^^^^^^^^^^

The typical flow for a draft email is:

1. **Generated**: pretalx creates the email automatically (e.g., when you accept a proposal) or you compose it manually
2. **Review**: You view the email in the drafts folder and verify the content
3. **Edit** (optional): You can modify the text, subject, or recipients if needed
4. **Send**: You explicitly send the email by clicking "Send" – either for individual emails or in bulk
5. **Sent**: The email is delivered and moves to the "Sent" tab for your records

Emails in the drafts folder can be deleted at any time before sending. Once sent,
they move to the sent mail history and cannot be edited or sent again.

Exceptions: Emails Sent Immediately
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A few email types are sent immediately without going to drafts, because they require
immediate action:

- **Organiser notifications** when a new proposal is submitted (if enabled in settings)
- **Speaker invitations** when you add a speaker with a new account (they need the password setup link immediately)
- **Team notifications** when you message reviewers or other team members

These exceptions are rare and clearly indicated in the interface.

Email Templates
---------------

Templates define the content of automatically generated emails. pretalx includes
default templates for common scenarios, and you can customize them to match your
event's voice and needs.

Built-in Template Types
^^^^^^^^^^^^^^^^^^^^^^^

pretalx provides templates for these scenarios:

**Proposal Workflow**
  - **Acknowledge Submission**: Sent when a speaker submits a proposal, confirming receipt
  - **Proposal Accepted**: Sent when you accept a proposal, asking the speaker to confirm
  - **Proposal Rejected**: Sent when you reject a proposal, notifying the speaker

**Schedule Management**
  - **New Schedule**: Sent when you release a new schedule version, notifying speakers of their scheduled time/room or changes

**Speaker Management**
  - **Add a Speaker (New Account)**: Sent when you add a speaker who doesn't have a pretalx account yet
  - **Add a Speaker (Existing Account)**: Sent when you add a speaker who already has an account

**Additional**
  - **Question Reminder**: Manually triggered to remind speakers to answer required questions
  - **New Submission (Organiser)**: Internal notification when a proposal is submitted (sent immediately, not to drafts)

Default vs Custom Templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you create an event, pretalx automatically generates **default templates** for
each template type. These provide sensible starting content with placeholder variables
for event-specific information.

You can **customize** any template by:

1. Going to **Settings → Mail → Templates**
2. Selecting the template you want to modify
3. Editing the subject and/or text
4. Saving your changes

Customized templates are used for all future emails of that type. You can also create
additional custom templates for manual email composition.

Template Placeholders
^^^^^^^^^^^^^^^^^^^^^

Templates use placeholders (variables) that are automatically replaced with actual
values when the email is generated. Placeholders are written in curly braces like
``{event_name}`` or ``{proposal_title}``.

Common placeholders include:

**Event Information**
  - ``{event_name}`` or ``{event}``: Your event's name
  - ``{event_url}``: URL to your event's main page

**Proposal Information** (for submission-related emails)
  - ``{proposal_title}``: The proposal's title
  - ``{proposal_url}``: Link to view the proposal
  - ``{speakers}``: Names of all speakers on the proposal
  - ``{track_name}``: The proposal's track (if tracks are enabled)
  - ``{confirmation_link}``: Link for speakers to confirm acceptance
  - ``{withdraw_link}``: Link for speakers to withdraw their proposal

**Schedule Information** (for schedule notification emails)
  - ``{session_start_date}``: When the session is scheduled
  - ``{session_start_time}``: Time the session starts
  - ``{session_room}``: Room assignment
  - ``{notifications}``: List of changes to the speaker's schedule

**Speaker Information**
  - ``{name}``: The recipient's full name
  - ``{email}``: The recipient's email address

When editing a template, you'll see the available placeholders listed in the interface.
You can use them anywhere in the subject or body of the template.

.. _`template-caveat`:

Templates and Existing Drafts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here's an important caveat about editing templates:

.. note::
    When you edit a template, **only newly generated emails** will use the updated
    text. **Emails already in your drafts folder keep their original content** and
    are not updated.

This is intentional – it prevents your existing draft emails from suddenly changing
when you modify a template. However, it means if you want draft emails to use your
new template text, you need to:

1. Delete the existing draft emails
2. Regenerate them using the updated template

You can regenerate acceptance/rejection emails from **Review → Actions → Regenerate emails**
and schedule notification emails from **Schedule → Actions → Resend schedule emails**.

Composing Manual Emails
------------------------

Beyond the automated templates, you can compose emails manually to communicate with
speakers, reviewers, or other groups.

Session Mail Composer
^^^^^^^^^^^^^^^^^^^^^^

The session mail composer (**Mail → Compose → To sessions/speakers**) lets you send
emails to speakers based on various criteria.

**Recipient Filtering**

You can send to speakers of proposals matching:

- **State**: Submitted, accepted, rejected, confirmed, withdrawn
- **Session type**: Filter by talk format (talk, workshop, etc.)
- **Track**: Filter by topic/track
- **Tags**: Filter by internal tags
- **Language**: Filter by proposal locale
- **Questions**: Filter by answer to specific proposal questions

Or you can select specific proposals and/or individual speakers from a list.

**Multi-Language Support**

If your event supports multiple languages, you can write your email in multiple
languages. pretalx will send each speaker the version that best matches their
preferred language (or your event's default language if their preference isn't available).

**Send Options**

After composing your email, you can:

- **Add to drafts**: Places the email(s) in your drafts folder for review before sending
- **Send immediately**: Skips the drafts folder and sends right away (use with caution)

The composer also handles deduplication automatically – if multiple proposals from
the same speaker match your filters, they'll only receive one email.

Team Mail Composer
^^^^^^^^^^^^^^^^^^^

The team mail composer (**Mail → Compose → To teams**) lets you send emails to
reviewers and other team members.

You can select which teams to send to, and the email will go to all members of
those teams. Team emails are always sent immediately (they don't go to drafts).

Draft Reminder Emails
^^^^^^^^^^^^^^^^^^^^^^

The draft reminders feature (**Mail → Draft reminders**) helps you remind speakers
who have incomplete proposals.

You can send a reminder to speakers who:

- Have draft proposals (started but not submitted)
- Have submitted proposals with unanswered required questions

These reminders are sent immediately to prompt quick action.

Sending and Managing Emails
----------------------------

Reviewing Drafts Before Sending
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before sending draft emails, review them in the drafts folder:

1. Click on an email to view its full content
2. Verify the recipient, subject, and message are correct
3. Use the preview feature to see how placeholders are filled in
4. Edit the email if needed (you can change any field)

Sending Emails
^^^^^^^^^^^^^^

You can send emails individually or in bulk:

**Individual Send**
  Open a draft email and click "Send". The email is sent immediately and moves to
  your sent mail history.

**Bulk Send**
  In the drafts list, select multiple emails using the checkboxes, then use the
  "Send selected emails" action. This is particularly useful after accepting/rejecting
  many proposals – you can review all the generated emails, then send them all at once.

Once sent, emails cannot be recalled or edited.

Sent Mail History
^^^^^^^^^^^^^^^^^

All sent emails appear in **Mail → Sent** where you can:

- Review what was sent and when
- See who received each email
- Copy a sent email to drafts to re-send similar content to other recipients

This provides a complete audit trail of your event communication.

Deleting Unwanted Drafts
^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't want to send a draft email, simply delete it from the drafts folder.
This is common when:

- You accepted proposals but want to rewrite the acceptance email
- You need to change templates before sending
- You made a mistake and want to regenerate the emails

You can delete individual emails or delete all emails generated from a specific
template at once.

Regenerating Emails
-------------------

Sometimes you need to recreate emails that were already generated – for example,
if you updated a template and want existing draft emails to use the new text, or
if you deleted drafts and need to generate them again.

Regenerating Acceptance/Rejection Emails
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To recreate state change notification emails:

1. Navigate to **Review → Actions → Regenerate emails**
2. Filter proposals by state, type, track, or other criteria
3. Select which proposals should have emails regenerated
4. Click "Regenerate" to create new draft emails

This creates fresh emails in your drafts folder using your current templates. If
you already have draft emails for these proposals, you may want to delete them first
to avoid duplicates.

Regenerating Schedule Notification Emails
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To recreate schedule change notifications:

1. Navigate to **Schedule → Actions → Resend schedule emails**
2. The system will generate emails for all speakers affected by your most recent schedule release
3. New draft emails are created with updated schedule information and calendar attachments

This is useful if you want to notify speakers again about their schedule, or if you
updated the schedule notification template and want to resend with the new text.

Email Settings
--------------

You can configure event-wide email settings under **Settings → Mail**.

Subject Prefix
^^^^^^^^^^^^^^

Add a prefix to all email subjects (e.g., ``[MyConf2024]``) to help recipients
identify your emails and filter them in their inbox. This prefix is automatically
added to every email sent from your event.

Signature
^^^^^^^^^

Set a signature that will be appended to all emails, typically including your
organization name, contact information, or social media links. The signature is
added automatically to every email.

New Submission Notifications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Enable organiser notifications to receive an immediate email whenever a speaker
submits a new proposal. This helps you stay informed about new submissions without
checking the system constantly.

.. note::
    Organiser notifications are sent immediately (not placed in drafts) so you can
    respond to submissions quickly.

Per-Template Settings
^^^^^^^^^^^^^^^^^^^^^

For each template, you can also configure:

- **Reply-To address**: Override where replies to this email type should go
- **BCC addresses**: Blind copy addresses for record-keeping or compliance

Common Workflows
----------------

Here are some common email workflows to help you use the system effectively:

Accepting Proposals
^^^^^^^^^^^^^^^^^^^

1. Review proposals and mark them as "accepted" from the review dashboard
2. pretalx generates acceptance emails in your drafts folder
3. Review the acceptance emails – verify the acceptance template text is appropriate
4. (Optional) Edit individual emails to personalize them
5. Send all acceptance emails at once using bulk send
6. Speakers receive their acceptance emails and can confirm their attendance

Releasing a Schedule
^^^^^^^^^^^^^^^^^^^^

1. Build your schedule in the schedule editor
2. Release a new schedule version, checking "Notify speakers"
3. pretalx generates schedule notification emails in drafts
4. Review the notification emails – they include session time, room, and calendar attachments
5. Send the notifications to inform speakers of their scheduled slots
6. Speakers receive their schedule information with calendar invites

Updating a Template
^^^^^^^^^^^^^^^^^^^

1. Go to **Settings → Mail → Templates** and edit the template
2. Save your changes
3. Navigate to your drafts folder and **delete** any existing emails you want to regenerate
4. Use the appropriate regenerate function to create new emails with the updated template
5. Review and send the regenerated emails

Remember: editing a template doesn't update existing drafts (see :ref:`template-caveat`),
so you must manually delete and regenerate if you want to use the new template text.

Best Practices
--------------

**Review Before Sending**
  Always review draft emails before sending, especially acceptance and rejection
  emails. A quick review catches mistakes and allows you to personalize messages.

**Use Bulk Send**
  After accepting or rejecting many proposals, review all the generated emails,
  then send them all at once. This ensures speakers are notified simultaneously
  rather than in dribs and drabs.

**Customize Templates Early**
  Set up your email templates early in your event setup, before you start accepting/
  rejecting proposals. This prevents needing to regenerate emails later.

**Keep Templates Professional**
  Remember that email templates represent your event. Keep them professional,
  friendly, and clear. Include all necessary information (deadlines, next steps, etc.)

**Test with Yourself First**
  Before sending important emails to all speakers, send a test email to yourself or
  a co-organiser to verify formatting and content.

**Monitor Sent Mail**
  Periodically review your sent mail history to ensure emails are being delivered
  and contain the correct information.

Next Steps
----------

After setting up your email communication:

- Learn about proposal states in the :ref:`Sessions Guide <user-guide-proposals>` to understand when acceptance/rejection emails are generated
- Review the :ref:`Review Guide <user-guide-review>` for information about the review process that leads to acceptance decisions
- Check the :ref:`Scheduling Guide <user-guide-schedule>` for details on schedule release and speaker notifications
