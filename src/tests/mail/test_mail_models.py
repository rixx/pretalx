# SPDX-FileCopyrightText: 2018-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms
#
# This file contains Apache-2.0 licensed contributions copyrighted by the following contributors:
# SPDX-FileContributor: Florian Moesch

import pytest
from django_scopes import scope

from pretalx.common.mail import TolerantDict
from pretalx.mail.models import QueuedMail


@pytest.mark.parametrize(
    "key,value",
    (
        ("1", "a"),
        ("2", "b"),
        ("3", "3"),
    ),
)
def test_tolerant_dict(key, value):
    d = TolerantDict({"1": "a", "2": "b"})
    assert d[key] == value


@pytest.mark.django_db
def test_sent_mail_sending(sent_mail):
    assert str(sent_mail)
    with pytest.raises(Exception):  # noqa
        sent_mail.send()


@pytest.mark.django_db
def test_mail_template_model(mail_template):
    assert mail_template.event.slug in str(mail_template)


@pytest.mark.parametrize("commit", (True, False))
@pytest.mark.django_db
def test_mail_template_model_to_mail(mail_template, commit):
    mail_template.to_mail("testdummy@exacmple.com", None, commit=commit)


@pytest.mark.django_db
def test_mail_template_model_to_mail_fails_without_address(mail_template):
    with pytest.raises(TypeError):
        mail_template.to_mail(1, None)


@pytest.mark.django_db
def test_mail_template_model_to_mail_shortens_subject(mail_template):
    mail_template.subject = "A" * 300
    mail = mail_template.to_mail("testdummy@exacmple.com", None, commit=False)
    assert len(mail.subject) == 199


@pytest.mark.django_db
def test_mail_submission_present_in_context(mail_template, submission, event):
    with scope(event=event):
        mail = mail_template.to_mail(
            "testdummy@exacmple.com",
            None,
            context_kwargs={"submission": submission},
        )
        mail.save()
        assert mail.submissions.all().contains(submission)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "text,signature,expected",
    (
        ("test", None, "test"),
        ("test", "sig", "test\n-- \nsig"),
        ("test", "-- \nsig", "test\n-- \nsig"),
    ),
)
def test_mail_make_text(event, text, signature, expected):
    if signature:
        event.mail_settings["signature"] = signature
        event.save()
    assert QueuedMail(text=text, event=event).make_text() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "text,prefix,expected",
    (
        ("test", None, "test"),
        ("test", "pref", "[pref] test"),
        ("test", "[pref]", "[pref] test"),
    ),
)
def test_mail_prefixed_subject(event, text, prefix, expected):
    if prefix:
        event.mail_settings["subject_prefix"] = prefix
        event.save()
    assert QueuedMail(text=text, subject=text, event=event).prefixed_subject == expected


@pytest.mark.django_db
def test_mail_make_html_no_line_breaks(event):
    """Test make_html doesn't convert single line breaks to <br>."""
    text = "Line one\nLine two\n\nParagraph two with **bold** text"
    mail = QueuedMail(text=text, subject="Test", event=event)
    html = mail.make_html()
    # Extract the content div to check just the rendered markdown
    content_start = html.find('<div class="content">')
    content_end = html.find("</div>", content_start)
    content = html[content_start:content_end]
    # Should not have <br> tags in the content (single line breaks)
    assert "<br" not in content
    # Should have bold formatting
    assert "<strong>bold</strong>" in content
    # Should have multiple paragraphs
    assert content.count("<p>") >= 2


@pytest.mark.django_db
def test_mail_make_html_with_links(event):
    """Test make_html creates absolute links (no redirects)."""
    text = "Visit https://example.com for more information"
    mail = QueuedMail(text=text, subject="Test", event=event)
    html = mail.make_html()
    # Should have the link
    assert "https://example.com" in html
    # Should NOT use safelink redirect in emails
    assert "/redirect/" not in html
