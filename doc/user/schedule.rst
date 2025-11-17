.. SPDX-FileCopyrightText: 2025-present Tobias Kunze
.. SPDX-License-Identifier: CC-BY-SA-4.0

.. _`user-guide-schedule`:

Scheduling
==========

The schedule is where your event comes together – taking accepted sessions and
arranging them across rooms and time slots to create your conference programme.
pretalx provides a visual schedule editor that makes it easy to build and adjust
your schedule through drag-and-drop.

.. important::
    The most important thing to understand about schedules in pretalx is that
    **changes only become public when you release a new schedule version**. You
    can experiment, rearrange sessions, and refine your schedule as much as you
    want – none of these changes will be visible to the public until you
    explicitly release them.

Understanding Schedule Versions
--------------------------------

pretalx uses a **versioning system** for schedules, similar to how software uses
version control. This gives you the freedom to work on your schedule without
accidentally publishing incomplete changes, and allows you to track the history
of how your schedule evolved.

Work-in-Progress vs Published Schedules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At any given time, you have two schedules:

**Work-in-Progress (WIP) Schedule**
  Your current draft. This is where you arrange sessions, add breaks, and make
  changes. Only organisers can see the WIP schedule – speakers and the public
  cannot access it. Think of this as your private workspace.

**Published Schedule**
  The most recent version you've released to the public. This is what appears on
  your event's public schedule page and what attendees see. It remains unchanged
  until you release a new version.

When you make changes to your schedule – moving a talk to a different time,
adding a break, changing a room – those changes are made to your WIP schedule
only. The published schedule stays exactly as it was.

Tracking Unreleased Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you've made changes to your WIP schedule that haven't been released yet, you'll
see a small indicator dot next to "Schedule" in the organiser sidebar. This serves
as a visual reminder that you have unpublished changes.

This is particularly useful when multiple organisers are working on the event, as
it makes it clear at a glance whether the current public schedule matches your
working version.

The Schedule Editor
-------------------

You can access the schedule editor under **Schedule → Schedule** in the organiser
interface. The editor provides a visual grid showing your rooms (as columns) and
time slots (as rows), with sessions appearing as blocks you can drag and drop.

Basic Scheduling
^^^^^^^^^^^^^^^^

To schedule a session:

1. Find the session in the "Unscheduled" panel on the right side
2. Drag it to the desired time slot and room in the grid
3. The session will snap to the grid, occupying the appropriate duration

To reschedule a session:

1. Drag it to a new time slot or room
2. pretalx will warn you about conflicts (speaker unavailability, room conflicts, etc.)

To unschedule a session:

1. Click on the session in the grid
2. Select "Remove from schedule" in the session details panel

Only sessions in the "confirmed" state will be visible to the public when you
release your schedule. Sessions in "accepted" state can be scheduled, but won't
appear publicly until the speakers confirm their attendance. See
:ref:`user-guide-proposals` for more about session states.

Editor Display Modes
^^^^^^^^^^^^^^^^^^^^

The schedule editor offers two display modes to accommodate different working styles
and event sizes:

**Expanded Mode** (default)
  Shows the full unscheduled session list with search and filtering options. Sessions
  appear larger in the grid, making it easier to read details. This mode is best when
  you're actively scheduling and need to see all available sessions.

**Condensed Mode**
  Compacts the grid to show more time slots and rooms at once. The unscheduled panel
  collapses to give you more space. This mode is particularly useful for events with
  many rooms, where you want an overview of the entire day at a glance.

You can toggle between modes using the button at the top of the editor. Your preference
is saved in your browser, so you'll stay in your chosen mode across sessions.

Timeline Granularity
^^^^^^^^^^^^^^^^^^^^

By default, the schedule editor shows time slots in 30-minute intervals. However, you
can zoom in to see finer time divisions when needed:

**Click on any time in the left timeline** to expand that section. The editor will
show 5-minute intervals for that time period, allowing you to schedule sessions at
precise times that don't align to the 30-minute grid.

For example, if you want to start a talk at 10:15 instead of 10:00 or 10:30, click
on "10:00" in the timeline. The editor will expand to show 10:00, 10:05, 10:10, 10:15,
etc., and you can drag your session to the 10:15 slot.

.. tip::
    This timeline expansion feature is easy to miss but extremely useful for fine-tuning
    your schedule. Look for the small arrow icons next to times in the timeline – these
    indicate expandable sections.

Session Details and Warnings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you click on a scheduled session, a details panel appears showing:

- The session title, speakers, and track
- The current room and time
- **Availability warnings** if speakers are marked as unavailable during that slot
- **Room warnings** if the room has availability constraints that conflict
- Options to reschedule or unschedule the session

These warnings help you avoid scheduling conflicts before they become problems.

.. _`schedule-breaks`:

Breaks and Schedule-Only Blocks
--------------------------------

Not everything in your schedule needs to be a session with speakers and content.
Breaks, meals, social events, and other organisational blocks can be added directly
to the schedule without going through the proposal workflow.

What Are Breaks?
^^^^^^^^^^^^^^^^

In pretalx terminology, a "break" is any schedule block that isn't tied to a session.
This includes:

- Lunch breaks
- Coffee breaks
- Registration periods
- Opening/closing ceremonies
- Social events
- Networking time
- Setup/teardown periods

Breaks appear in the public schedule just like sessions, but with important differences:

- They have a **grey/muted appearance** to distinguish them from sessions
- They have **no detail page** – clicking on them doesn't go anywhere
- They have **no speakers** or speaker information
- They can have a title and optional description in multiple languages
- They're typically shown across **multiple rooms** (e.g., lunch is available everywhere)

Creating Breaks
^^^^^^^^^^^^^^^

To create a break:

1. Click the **"+ New Break"** button in the unscheduled panel
2. Drag the new break to the desired time slot in the schedule grid
3. Click on the break to edit its details (title, duration, description)

By default, breaks are 5 minutes long, but you can adjust the duration to anything
you need.

Scheduling Breaks Across Multiple Rooms
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Breaks often need to appear in multiple rooms simultaneously (like a lunch break that
applies to the entire event). To schedule a break across rooms:

1. Create and schedule the break in one room
2. Click on the break to open the details panel
3. Use the **"Copy to other rooms"** option to place it in additional rooms

Each copy is independent, so if you need to adjust the break later, you'll need to
update each room individually (or delete and recreate).

When to Use Breaks vs Sessions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use a **break** when:

- There are no speakers or content creators to credit
- Attendees don't need detailed information beyond "this is happening"
- The item is organisational rather than content-focused

Use a **session** when:

- There are speakers who should be credited
- The content deserves its own detail page with description and metadata
- You want to collect the content through the CfP or create it as a proposal

For example, a "Welcome Address" might work better as a session (with speakers) while
"Registration Opens" works better as a break (no speakers, just an announcement).

Releasing Schedule Versions
----------------------------

Once you're happy with your WIP schedule, you can release it as a new version to make
it visible to the public.

Before You Release
^^^^^^^^^^^^^^^^^^

Navigate to **Schedule → Release new schedule version**. Before releasing, pretalx
will show you warnings about potential issues:

**Talk Warnings**
  Sessions that have scheduling conflicts:

  - Speaker unavailable during the scheduled time
  - Room unavailable during the scheduled time
  - Multiple talks in the same room at the same time
  - A speaker scheduled for multiple talks at overlapping times

**Unscheduled Talks**
  Confirmed sessions that haven't been placed in the schedule yet. These sessions
  won't appear in the public schedule until you schedule and release them.

**Unconfirmed Talks**
  Sessions that are scheduled but not yet confirmed by their speakers. These will
  be scheduled in the grid but **won't be visible to the public** – only the
  organisers will see them. This allows you to plan your schedule before all speakers
  have confirmed, but prevents announcing sessions that might be cancelled.

**Missing Information**
  Sessions that are missing required information like track assignments (if your
  event uses tracks).

You can proceed with releasing the schedule even if there are warnings, but it's
worth reviewing them to avoid publishing a schedule with known conflicts.

Creating the Release
^^^^^^^^^^^^^^^^^^^^^

To release a new schedule version, you need to provide:

**Version Name** (required)
  A unique identifier for this version, like "v1.0", "v2.0", "final", "2024-11-17",
  etc. Choose whatever naming scheme makes sense for your event. The version name
  will be shown in the public schedule changelog, so attendees can see what version
  they're viewing.

**Change Summary** (optional)
  A description of what changed in this release. This appears in the public changelog
  at ``/{event}/schedule/changelog/``, where attendees can see the evolution of your
  schedule. For example: "Moved keynote to main hall, added coffee breaks, swapped
  two workshop times."

**Notify Speakers** (optional)
  Check this box to send email notifications to speakers whose sessions were affected
  by this release. Speakers will be notified about:

  - **New scheduled sessions**: Their talk has been scheduled for the first time
  - **Moved sessions**: Their talk changed time or room since the last release

  Notifications are only sent for **visible sessions** (confirmed talks), and each
  speaker receives a single email listing all their affected sessions.

What Happens During Release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you release a schedule:

1. A new **published schedule** is created with your version name and timestamp
2. Your current **WIP schedule** is duplicated to become the new published version
3. A **new empty WIP schedule** is created for your next round of changes
4. Only **confirmed sessions** become visible to the public – accepted but unconfirmed sessions remain hidden
5. **Breaks** that are scheduled become visible to the public
6. If you enabled notifications, speaker emails are generated and placed in your drafts folder
7. The unreleased changes indicator disappears from the sidebar

The public can now see your new schedule at ``/{event}/schedule/``.

After Release: Making More Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After releasing, your WIP schedule starts as a copy of what you just released. Any
changes you make from this point forward will be to the new WIP, and won't affect
the public schedule until you release again.

This means you can:

- Fix mistakes immediately without creating a new public version
- Experiment with different arrangements
- Gradually make changes over several days before releasing
- Respond to last-minute changes without pressure

When you have a batch of changes ready, release a new version. The version name
should be different from previous releases (e.g., if you just released "v1.0", your
next release might be "v1.1" or "v2.0").

Previewing Your Schedule
-------------------------

Before releasing, you'll want to see what your schedule will look like to the public.

Preview as an Organiser
^^^^^^^^^^^^^^^^^^^^^^^

As an organiser, when you visit your event's public schedule page at
``/{event}/schedule/``, you'll see the most recent **published** schedule – the same
view attendees see.

To preview your **WIP schedule**, navigate to the schedule editor (**Schedule → Schedule**).
The grid view shows your work-in-progress exactly as it will appear after release
(though with all sessions visible, including unconfirmed ones marked with indicators).

Understanding What's Public
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Remember that the public schedule only shows:

- The most recently **released** version
- Only **confirmed** sessions (not just accepted ones)
- Breaks that were scheduled when you released
- Rooms that have scheduled content

If you've scheduled sessions but haven't released, or if sessions are only "accepted"
but not "confirmed", they won't appear on the public schedule even after release.

Schedule Changelog
^^^^^^^^^^^^^^^^^^

The public can view your schedule changelog at ``/{event}/schedule/changelog/``.
This page lists all versions you've released, their timestamps, and the change
summaries you provided. It also shows the detailed changes (new talks, moved talks,
cancelled talks) for each version.

This transparency helps attendees stay informed about schedule changes and plan
accordingly.

Resetting Your Schedule
------------------------

If you've made changes to your WIP schedule and want to discard them, you can reset
back to a previous published version:

1. Navigate to **Schedule → Reset current schedule**
2. Select which published version you want to reset to
3. Confirm the reset

Your WIP schedule will be replaced with a copy of the selected version. **This cannot
be undone**, so use this feature carefully. However, it's very useful if you've
experimented with a major rearrangement and decided you prefer an earlier version.

Rooms and Availability
-----------------------

Rooms are the physical or virtual spaces where sessions take place. You can manage
rooms under **Settings → Rooms**.

Room Configuration
^^^^^^^^^^^^^^^^^^

Each room has:

- A **name** (e.g., "Main Hall", "Workshop Room A")
- Optional **capacity** (for tracking attendee limits)
- Optional **description** and **speaker information** (notes shown to speakers assigned to this room)
- **Availability** constraints (optional time windows when the room can be used)

Rooms appear as columns in the schedule editor, ordered left-to-right by their
position setting.

Room Availability
^^^^^^^^^^^^^^^^^

If your venue has time constraints (e.g., certain rooms are only available in the
afternoon), you can set room availability:

1. Edit the room in **Settings → Rooms**
2. Add availability windows specifying when the room is available
3. The schedule editor will warn you if you try to schedule sessions outside these windows

This is particularly useful for multi-venue events or when rooms have dedicated purposes
during certain times.

Embedding Your Schedule
-----------------------

Once your schedule is published, you can embed it on your event website using the
pretalx widget. This allows attendees to view your schedule without leaving your site.

The widget displays your public schedule and automatically updates when you release
new versions, so your website always shows the current schedule.

Learn more in the :ref:`widget guide <user-guide-widget>`.

Next Steps
----------

After building your schedule, you might want to:

- Review session states in the :ref:`Sessions Guide <user-guide-proposals>` to understand how to move sessions through the acceptance workflow
- Set up speaker communications in the :ref:`Email Guide <user-guide-emails>` to notify speakers about their scheduled sessions
- Configure the embeddable widget in the :ref:`Widget Guide <user-guide-widget>` to show your schedule on your event website
