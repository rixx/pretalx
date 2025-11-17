.. SPDX-FileCopyrightText: 2025-present Tobias Kunze
.. SPDX-License-Identifier: CC-BY-SA-4.0

.. _`user-guide-review`:

Reviews
=======

Reviews help you evaluate and select proposals for your event. The review process
in pretalx is highly configurable, allowing you to adapt it to your event's needs
– from a simple voting system to complex multi-stage reviews with detailed scoring.

The Basics
----------

At its core, a review is an evaluation of a proposal by a user with review permissions.
Reviews typically consist of:

- **Scores**: Numeric ratings based on categories you define (e.g., "Content Quality", "Presentation")
- **Text feedback**: Written comments explaining the reviewer's assessment

Reviews are distinct from comments (see :ref:`comments-vs-reviews` below) in that
they are structured, scored evaluations that only reviewers can submit, and that
speakers cannot see. Each reviewer can only submit one review per proposal, though
they can edit their review at any time (depending on your review phase settings).

The review data helps you make acceptance decisions, typically through the review
dashboard where you can see aggregated scores and sort proposals by various criteria.

Setting up Review Phases
-------------------------

Review phases define the rules and permissions for a period of review. You can have
multiple sequential review phases, which is useful for multi-stage review processes
(e.g., an initial screening phase followed by a detailed evaluation phase).

You can configure review phases under **Settings → Review**.

Basic Configuration
^^^^^^^^^^^^^^^^^^^

Each review phase has a name, an optional description, and optional start and end dates.
If you don't set dates, the phase is always active. If you have multiple phases, pretalx
will automatically use the currently active phase based on the dates.

The phase configuration determines what reviewers can do during that phase:

Review Permissions
^^^^^^^^^^^^^^^^^^

**Can reviewers write reviews?**
  Controls whether reviewers can submit new reviews or edit existing ones during this
  phase. You might disable this during a decision-making phase when you want reviewers
  to only view results without making changes.

**Can reviewers change submission states?**
  If enabled, reviewers can accept or reject proposals directly. This is useful if you
  want to distribute the decision-making process, but you may prefer to keep this
  centralised with organisers only.

**Can reviewers see other reviews?**
  Three options control when reviewers can see what their peers have written:

  - **Always**: Reviewers see all reviews immediately
  - **After submitting their own review**: Prevents anchoring bias by hiding other reviews until the reviewer has formed their own opinion
  - **Never**: Reviews remain private, useful for independent evaluation

Visibility Settings
^^^^^^^^^^^^^^^^^^^

**Reviewers may see these proposals**
  This is a crucial setting that determines which proposals reviewers can access:

  - **All proposals**: Reviewers see all proposals their teams have access to. If a proposal is assigned to them specifically, it will be highlighted and shown first in their review list.
  - **Only assigned proposals**: Reviewers can only see proposals that have been explicitly assigned to them. This is essential when you want reviewers to evaluate a specific subset without seeing the full proposal pool.

**Can reviewers see speaker names?**
  When disabled, reviewers see anonymised speaker information, helping to reduce bias
  in the review process. See :ref:`review-anonymisation` below for more details.

**Can reviewers see reviewer names?**
  When disabled, reviewers cannot see who wrote which review, useful for preventing
  social dynamics from influencing evaluations.

Editing and Organisation
^^^^^^^^^^^^^^^^^^^^^^^^^

**Allow speakers to edit their proposals**
  Controls whether speakers can modify their proposals during the review phase. Once
  the CfP is closed, this setting takes over from the CfP-level editing permissions.
  You might disable this during active review to prevent proposals from changing while
  being evaluated.

**Can reviewers tag submissions?**
  Three options allow different levels of organisational tagging:

  - **Never**: Reviewers cannot add or use tags
  - **Use existing tags**: Reviewers can apply tags that organisers have created
  - **Create new tags**: Reviewers can create and apply their own tags

  Tags are useful for categorisation and filtering, but remain internal – they are
  never shown to speakers or the public.

Setting up Review Scores
-------------------------

Review scores are the numeric ratings that reviewers assign to proposals. You can
configure multiple score categories, each measuring a different aspect of the proposal.

Score Categories
^^^^^^^^^^^^^^^^

Each event can have multiple score categories, which you configure under
**Settings → Review**. Common examples include:

- Content Quality
- Speaker Experience
- Audience Interest
- Clarity of Description

For each category, you define the possible scores (e.g., "Poor", "Fair", "Good",
"Excellent") along with their numeric values.

Score Weights
^^^^^^^^^^^^^

Each score category has a **weight** that determines its influence on the total score.
For example, if you consider "Content Quality" more important than "Clarity of Description",
you might give it a weight of 2.0 while the other has 1.0.

The total score for a review is calculated as::

    total = (score₁ × weight₁) + (score₂ × weight₂) + ... + (scoreₙ × weightₙ)

Independent Scores
^^^^^^^^^^^^^^^^^^

Sometimes you want to collect certain ratings separately without including them in
the total score. For example, you might want to track "Beginner-Friendliness" as
additional information without it affecting the overall evaluation.

When you mark a score category as **independent**, it:

- Has its weight automatically set to 0
- Is excluded from the total score calculation
- Appears as a separate column in the review dashboard
- Is averaged independently across all reviews

This allows you to collect supplementary information while keeping your main evaluation
focused on the primary criteria.

Normal (Aggregate) Scores
^^^^^^^^^^^^^^^^^^^^^^^^^^

Non-independent scores are aggregated using their weights to produce a total score
for each review. This total score is then used in the dashboard's sorting and
aggregation features.

For example, with two categories:

- Content Quality (weight: 2.0): rated 4/5
- Presentation (weight: 1.0): rated 3/5

The total would be: (4 × 2.0) + (3 × 1.0) = 11 points

Track-Specific Scores
^^^^^^^^^^^^^^^^^^^^^

You can limit certain score categories to specific tracks. This is useful when different
types of sessions need different evaluation criteria – for example, workshops might need
a "Hands-on Quality" score that talks don't require.

.. _`review-anonymisation`:

Anonymisation
-------------

Anonymisation helps reduce unconscious bias in the review process by hiding speaker
identities from reviewers. pretalx supports partial anonymisation, allowing you to
hide identifying information while keeping the proposal content intact.

How Anonymisation Works
^^^^^^^^^^^^^^^^^^^^^^^^

When you anonymise a proposal, you can edit specific fields to remove identifying
information:

- Title
- Abstract
- Description
- Notes

For each field, you only need to provide an anonymised version if it contains
identifying information. Fields you don't modify will show their original content
to reviewers.

For example, a title like "Building Web Apps with React: Lessons from My Startup"
might be anonymised to "Building Web Apps with React: Lessons Learned" to remove
the reference to a specific company.

The original content is preserved, and speakers always see their original submission
unchanged. Only reviewers (when the review phase has "Can reviewers see speaker names"
disabled) see the anonymised version.

Enabling Anonymised Reviews
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To conduct anonymised reviews:

1. Disable **"Can reviewers see speaker names"** in your active review phase settings
2. Navigate to the proposals list and select proposals to anonymise
3. For each proposal, edit the anonymised fields to remove identifying information
4. A "Save and go to next unanonymised" button helps you quickly work through proposals

.. note::
    Anonymisation is optional – you can enable the "can't see speaker names" setting
    without creating anonymised versions. In this case, reviewers simply won't see
    the speaker names and profiles, but the proposal content remains unchanged.

Review Assignments and Permissions
-----------------------------------

Review permissions are controlled through teams, while assignments direct specific
reviewers to specific proposals.

Teams and Permissions
^^^^^^^^^^^^^^^^^^^^^^

To give someone review access, add them to a team with the **Reviewer** permission.
You can create teams under **Settings → Teams**.

Teams can have various permission levels. For review workflows, the key consideration
is whether the team has *only* reviewer permissions or additional permissions:

- **Only reviewer permissions**: Team members can only see proposals they have access to based on the review phase "Reviewers may see these proposals" setting
- **Additional permissions** (e.g., proposal editing): Team members can see all proposals regardless of assignments or review phase settings

Track-Based Teams
^^^^^^^^^^^^^^^^^

Teams can be limited to specific tracks. If your event uses tracks, you can create
separate reviewer teams for each track, ensuring that reviewers only see proposals
in their domain of expertise.

For example:

- "Security Track Reviewers" → can only review proposals in the Security track
- "Web Development Reviewers" → can only review proposals in the Web Development track

Assigning Reviewers to Proposals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Beyond track-based and team-based access, you can assign specific reviewers to
specific proposals. This is useful for:

- Ensuring each proposal gets reviewed by domain experts
- Distributing review workload evenly
- Implementing specialised review workflows

There are two ways to create assignments:

Manual Assignment
"""""""""""""""""

Navigate to **Review → Assign Reviewers** where you can:

- **Assign reviewers to proposals**: Select a proposal, then choose which reviewers should review it
- **Assign proposals to reviewers**: Select a reviewer, then choose which proposals they should review

The interface shows you the current assignment status and helps you balance the
workload across reviewers.

Bulk Import
"""""""""""

For larger events or pre-planned assignments, you can import assignments via JSON file
through the **Actions** menu. The format is simple::

    {
        "reviewer@example.org": ["PROPOSAL1", "PROPOSAL2"],
        "other@example.org": ["PROPOSAL3"]
    }

Or reversed (proposals to reviewers)::

    {
        "PROPOSAL1": ["reviewer@example.org", "other@example.org"],
        "PROPOSAL2": ["reviewer@example.org"]
    }

You can download :download:`review-assignments.json` as a template.

How Assignments Work
""""""""""""""""""""

Assignments interact with the review phase visibility setting:

- **"All proposals" visibility**: Assigned proposals are highlighted and sorted first in the reviewer's list, but they can still see and review other proposals
- **"Only assigned proposals" visibility**: Reviewers can **only** access their assigned proposals, making this the key setting for controlled review workflows

The Review Flow
---------------

Once your review phases and scores are configured, the review process typically
follows this flow:

1. Organisers invite reviewers by adding them to teams with reviewer permissions
2. Reviewers access the review dashboard and see their assigned (or all available) proposals
3. Reviewers evaluate proposals and submit their reviews with scores and text
4. Organisers monitor progress through the review dashboard
5. Organisers use aggregated scores to make acceptance decisions
6. Proposals are moved to accepted/rejected states (see :ref:`user-guide-proposals`)

.. _`review-dashboard`:

The Review Dashboard
^^^^^^^^^^^^^^^^^^^^

The review dashboard is the central hub for the review process. Organisers see the
full dashboard at **Review → Reviews**, while reviewers see their personalised view.

**For reviewers**, the dashboard shows:

- Proposals they can review (based on assignments, teams, and visibility settings)
- Their own scores and review status for each proposal
- Aggregated scores from other reviewers (depending on "can see other reviews" settings)

**For organisers**, the dashboard additionally shows:

- Complete review statistics for all proposals
- Filtering and sorting by review count, scores, and other criteria
- Bulk actions for accepting/rejecting proposals

Key Dashboard Metrics
""""""""""""""""""""""

**Review Count**
  Shows the total number of reviews for each proposal, helping you identify
  proposals that need more attention.

**Aggregate Score** (Median or Average)
  The combined evaluation from all reviewers. You choose between two aggregation methods
  in **Settings → Review Settings**:

  - **Median**: The middle value when all review scores are sorted. More resistant to outliers – if one reviewer gives an unusually high or low score, it has less impact. For example, scores [3, 7, 8, 8, 9] have a median of 8.
  - **Average (Mean)**: The arithmetic mean of all review scores. Every review contributes equally to the final number. The same scores [3, 7, 8, 8, 9] have an average of 7.0.

  Choose median when you want to reduce the impact of divergent opinions, or mean
  when you want every review to contribute proportionally to the aggregate.

**Independent Score Columns**
  Categories marked as independent appear in separate columns, each showing the
  average rating across all reviews. This gives you quick insight into supplementary
  metrics without cluttering the main score.

**User Score**
  For reviewers viewing the dashboard, this column shows their own score for each
  proposal, making it easy to see which proposals they've reviewed and how they rated them.

Dashboard Actions
"""""""""""""""""

From the dashboard, you can:

- Click on a proposal to see its details, reviews, and comments
- Filter by track, submission type, state, or review status
- Sort by any column, including aggregate scores and review counts
- Select multiple proposals to bulk change their state to accepted/rejected
- Export the review data for external analysis

Working with Proposals
^^^^^^^^^^^^^^^^^^^^^^

When you open a proposal from the dashboard, you'll see several tabs:

**Content**
  The proposal details, as submitted by the speaker (or anonymised, if configured)

**Reviews**
  All reviews for this proposal (if you have permission to see them). Each review
  shows the reviewer's name (if not anonymised), their scores for each category,
  and their written feedback.

**Comments**
  The discussion thread for this proposal. See :ref:`comments-vs-reviews` below.

**Speakers**
  Information about the speakers (hidden during anonymised review)

Reviewers navigate to proposals from their dashboard, review the content, and submit
their evaluation through the review form showing their configured score categories
and an optional text field.

.. _`comments-vs-reviews`:

Comments vs Reviews
-------------------

pretalx provides two distinct ways to discuss proposals: comments and reviews. While
they may seem similar, they serve different purposes and have different rules.

Reviews
^^^^^^^

Reviews are **structured evaluations** used for the formal review process:

- **One per reviewer**: Each reviewer can submit only one review per proposal (though they can edit it)
- **Contains scores**: Reviews include numeric ratings based on your score categories
- **Private**: Reviews are **never visible to speakers**, even if the speakers have review permissions for other proposals
- **Structured feedback**: The combination of scores and text provides quantifiable data for decision-making
- **Requires reviewer permission**: Only users with the reviewer permission can submit reviews

Reviews are the primary tool for evaluation and selection.

Comments
^^^^^^^^

Comments are **discussions** about the proposal:

- **Multiple allowed**: Anyone can post as many comments as they want
- **No scores**: Comments are purely textual
- **Visible to all with access**: Comments can be read by organisers, reviewers, and depending on settings, even speakers
- **Conversational**: Comments are ordered by time like a forum thread, supporting back-and-forth discussion
- **Available to all with access**: Anyone who can see the proposal can comment (organisers and reviewers)

Comments are useful for:

- Asking speakers to clarify parts of their proposal
- Discussing edge cases with other reviewers
- Documenting conversations or decisions about the proposal
- Noting why certain decisions were made

.. note::
    You can enable submission comments separately in your event settings. If disabled,
    the comments feature won't be available.

When to Use Each
^^^^^^^^^^^^^^^^

Use **reviews** when you need to:

- Formally evaluate a proposal for acceptance
- Provide scored, structured feedback
- Keep your evaluation private from speakers

Use **comments** when you need to:

- Ask the speaker a question
- Discuss the proposal with other reviewers
- Document a decision or conversation
- Add a note for future reference

Both comments and reviews are timestamped, preserving a complete history of your
event's review process.

Next Steps
----------

Once you've completed your review process and made your decisions, you'll want to
notify speakers and move forward with scheduling:

- See :ref:`user-guide-proposals` for information about proposal states (submitted, accepted, rejected, confirmed)
- See :ref:`user-guide-schedule` for information about building your event schedule
- See :ref:`user-guide-emails` for information about communicating with speakers
