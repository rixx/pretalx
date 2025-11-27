# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from django import template

from pretalx.submission.rules import filter_answers_by_team_access

register = template.Library()


@register.filter
def filter_team_answers(answers, user):
    """Filter answers based on team limits for questions.

    Usage: {{ submission.answers.all|filter_team_answers:request.user }}
    """
    if not answers:
        return answers
    return filter_answers_by_team_access(answers, user)
