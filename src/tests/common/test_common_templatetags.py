# SPDX-FileCopyrightText: 2018-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import pytest
from django_scopes import scope

from pretalx.common.templatetags.copyable import copyable
from pretalx.common.templatetags.html_signal import html_signal
from pretalx.common.templatetags.rich_text import (
    render_markdown_abslinks,
    rich_text,
)
from pretalx.common.templatetags.times import times
from pretalx.common.templatetags.xmlescape import xmlescape


@pytest.mark.parametrize(
    "number,output",
    (
        (1, "once"),
        (2, "twice"),
        (3, "3 times"),
        (None, ""),
        (0, "0 times"),
        ("1", "once"),
        ("2", "twice"),
        ("3", "3 times"),
    ),
)
def test_common_templatetag_times(number, output):
    assert times(number) == output


@pytest.mark.parametrize(
    "input_,output",
    (
        ("i am a normal string ??!!$%/()=?", "i am a normal string ??!!$%/()=?"),
        ("<", "&lt;"),
        (">", "&gt;"),
        ('"', "&quot;"),
        ("'", "&apos;"),
        ("&", "&amp;"),
        ("a\aa", "aa"),
        ("ä", "&#228;"),
    ),
)
def test_common_templatetag_xmlescape(input_, output):
    assert xmlescape(input_) == output


@pytest.mark.parametrize(
    "text,richer_text,noopener",
    (
        ("foo.notatld", "foo.notatld", False),
        (
            "foo.com",
            "//foo.com",
            True,
        ),
        ("foo@bar.com", "mailto:foo@bar.com", False),
        (
            "chaos.social",
            "//chaos.social",
            True,
        ),
    ),
)
def test_common_templatetag_rich_text(text, richer_text, noopener):
    result = rich_text(text)
    assert richer_text in result
    assert ('rel="noopener"' in result) is noopener
    assert ('target="_blank"' in result) is noopener


@pytest.mark.parametrize(
    "value,copy",
    (
        ('"foo', '"foo'),
        (
            "foo",
            """
    <span data-destination="foo"
            class="copyable-text"
            data-toggle="tooltip"
            data-placement="top"
            title="Copy"
    >
        foo
    </span>""",
        ),
    ),
)
def test_common_templatetag_copyable(value, copy):
    assert copyable(value) == copy


@pytest.mark.django_db
@pytest.mark.parametrize("slug", (True, False))
@pytest.mark.parametrize("signal", ("html_head", "html_above_profile_page"))
def test_html_signal(event, slug, signal):
    with scope(event=event):
        if slug:
            event.slug = "ignore_signal"
        event.plugins = "tests"
        event.save()
        result = html_signal(
            f"pretalx.cfp.signals.{signal}", sender=event, request=None
        )
        assert bool(result) is not slug


class MockEncodeDict(dict):
    def urlencode(self, **kwargs):
        return self

    def copy(self):
        return self


class FakeRequest:
    def __init__(self, get):
        self.GET = MockEncodeDict(get)


def test_email_markdown_no_line_breaks():
    """Test email markdown doesn't convert single line breaks to <br>."""
    text = "Line one\nLine two\n\nParagraph two"
    result = render_markdown_abslinks(text)
    # Single line breaks should not produce <br> tags in email rendering
    assert "<br" not in result
    # Double line breaks should still create separate paragraphs
    assert result.count("<p>") == 2


def test_web_markdown_has_line_breaks():
    """Test web markdown converts single line breaks to <br> tags."""
    text = "Line one\nLine two"
    result = rich_text(text)
    # Web rendering should convert single line breaks to <br> tags
    assert "<br" in result


def test_email_markdown_preserves_formatting():
    """Test email markdown preserves bold, italic, and formatting."""
    text = "**bold** and *italic* and ~~strikethrough~~"
    result = render_markdown_abslinks(text)
    assert "<strong>bold</strong>" in result
    assert "<em>italic</em>" in result
    assert "<del>strikethrough</del>" in result


def test_email_markdown_lists():
    """Test email markdown handles lists correctly."""
    text = (
        "Items:\n\n- First item\n- Second item\n\n"
        "1. Numbered one\n2. Numbered two"
    )
    result = render_markdown_abslinks(text)
    assert "<ul>" in result
    assert "<li>First item</li>" in result
    assert "<ol>" in result
    assert "<li>Numbered one</li>" in result


def test_email_markdown_links():
    """Test email markdown creates absolute links (no redirects)."""
    text = "Visit https://example.com for more info"
    result = render_markdown_abslinks(text)
    # Should create a link
    assert "<a" in result
    assert "https://example.com" in result
    # Should NOT use safelink redirect
    assert "/redirect/" not in result


def test_email_markdown_code_blocks():
    """Test that email markdown handles code blocks."""
    text = "Example:\n\n```\ncode here\n```"
    result = render_markdown_abslinks(text)
    assert "<pre>" in result or "<code>" in result


def test_email_markdown_empty_text():
    """Test that email markdown handles empty text gracefully."""
    assert render_markdown_abslinks("") == ""
    assert render_markdown_abslinks(None) == ""


def test_email_markdown_multiple_paragraphs():
    """Test that email markdown creates separate paragraphs correctly."""
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    result = render_markdown_abslinks(text)
    # Should have 3 paragraphs
    assert result.count("<p>") == 3
    # But no <br> tags for single line breaks within paragraphs
    assert "<br" not in result


def test_rich_text_abslinks_filter():
    """Test the rich_text_abslinks template filter directly."""
    from pretalx.common.templatetags.rich_text import rich_text_abslinks

    text = "Line one\nLine two\n\nhttps://example.com"
    result = rich_text_abslinks(text)
    # Should not have <br> tags
    assert "<br" not in result
    # Should have absolute link
    assert "https://example.com" in result
