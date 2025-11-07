# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import pytest
from django.template import Context, Template
from django_scopes import scope

from pretalx.submission.models import Question, QuestionVariant


@pytest.mark.django_db
def test_history_sidebar_template_tag_renders(event, orga_user):
    """Test that the history sidebar template tag renders correctly."""
    with scope(event=event):
        # Create a question
        question = Question.objects.create(
            event=event,
            question="Test Question",
            variant=QuestionVariant.STRING,
            target="submission",
        )

        # Log an action
        question.log_action(
            "pretalx.question.create",
            person=orga_user,
            orga=True,
            data={"question": "Test Question"},
        )

        # Render the template tag
        template = Template(
            "{% load history_sidebar %}{% history_sidebar object %}"
        )
        context = Context({"object": question, "request": type('Request', (), {"user": orga_user, "event": event})()})
        rendered = template.render(context)

        assert "Recent Changes" in rendered
        assert "added" in rendered.lower() or "created" in rendered.lower()


@pytest.mark.django_db
def test_history_sidebar_respects_limit(event, orga_user):
    """Test that the history sidebar respects the limit parameter."""
    with scope(event=event):
        # Create a question
        question = Question.objects.create(
            event=event,
            question="Test Question",
            variant=QuestionVariant.STRING,
            target="submission",
        )

        # Log multiple actions
        for i in range(15):
            question.log_action(
                f"pretalx.question.update.{i}",
                person=orga_user,
                orga=True,
                data={"iteration": i},
            )

        # Render with default limit (10)
        template = Template(
            "{% load history_sidebar %}{% history_sidebar object %}"
        )
        context = Context({"object": question, "request": type('Request', (), {"user": orga_user, "event": event})()})
        rendered = template.render(context)

        # Should have limited number of entries (not all 15)
        # Count occurrences of list items
        assert rendered.count("<li class=\"list-group-item logentry compact\">") == 10

        # Test with custom limit
        template = Template(
            "{% load history_sidebar %}{% history_sidebar object 5 %}"
        )
        rendered = template.render(context)
        assert rendered.count("<li class=\"list-group-item logentry compact\">") == 5


@pytest.mark.django_db
def test_history_sidebar_shows_change_details_link(event, orga_user):
    """Test that the history sidebar shows a link to change details when available."""
    with scope(event=event):
        # Create a question
        question = Question.objects.create(
            event=event,
            question="Test Question",
            variant=QuestionVariant.STRING,
            target="submission",
        )

        # Log an action with changes
        question.log_action(
            "pretalx.question.update",
            person=orga_user,
            orga=True,
            old_data={"question": "Old Question"},
            new_data={"question": "New Question"},
        )

        # Render the template tag
        template = Template(
            "{% load history_sidebar %}{% history_sidebar object %}"
        )
        context = Context({"object": question, "request": type('Request', (), {"user": orga_user, "event": event})()})
        rendered = template.render(context)

        # Should have a link to the detail view
        assert "event.history.detail" in rendered or "fa-search" in rendered


@pytest.mark.django_db
def test_history_sidebar_requires_authentication(event):
    """Test that the history sidebar doesn't show for unauthenticated users."""
    with scope(event=event):
        # Create a question
        question = Question.objects.create(
            event=event,
            question="Test Question",
            variant=QuestionVariant.STRING,
            target="submission",
        )

        # Render without authenticated user
        template = Template(
            "{% load history_sidebar %}{% history_sidebar object %}"
        )
        context = Context({"object": question, "request": type('Request', (), {"user": type('AnonymousUser', (), {"is_authenticated": False})()})()})
        rendered = template.render(context)

        # Should not show history
        assert "Recent Changes" not in rendered


@pytest.mark.django_db
def test_history_sidebar_on_question_detail_view(orga_client, event, orga_user):
    """Test that the history sidebar appears on the question detail view."""
    with scope(event=event):
        # Create a question
        question = Question.objects.create(
            event=event,
            question="Test Question",
            variant=QuestionVariant.STRING,
            target="submission",
            active=True,
        )

        # Log an action
        question.log_action(
            "pretalx.question.create",
            person=orga_user,
            orga=True,
            data={"question": "Test Question"},
        )

        # Access the question detail view
        url = f"/orga/event/{event.slug}/cfp/questions/{question.pk}/"
        response = orga_client.get(url)

        assert response.status_code == 200
        assert "Recent Changes" in response.content.decode()
