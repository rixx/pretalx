# SPDX-FileCopyrightText: 2024-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import pytest

from pretalx.common.social_preview import (
    generate_and_cache_speaker_preview,
    generate_and_cache_submission_preview,
    generate_speaker_preview,
    generate_submission_preview,
    get_cached_preview,
    get_settings_hash,
    invalidate_preview_cache,
)


@pytest.mark.django_db
def test_default_social_preview_settings(event):
    """Test that events have default social preview settings."""
    assert "submission" in event.social_preview_settings
    assert "speaker" in event.social_preview_settings
    assert event.social_preview_settings["submission"]["layout"] == "default"
    assert event.social_preview_settings["speaker"]["layout"] == "default"


@pytest.mark.django_db
def test_generate_submission_preview_default_layout(event, submission):
    """Test generating a submission preview with default layout."""
    img = generate_submission_preview(event, submission)
    assert img is not None
    assert img.size == (1200, 630)
    assert img.mode == "RGB"


@pytest.mark.django_db
def test_generate_submission_preview_minimal_layout(event, submission):
    """Test generating a submission preview with minimal layout."""
    settings_dict = {"layout": "minimal", "show_event_name": True}
    img = generate_submission_preview(event, submission, settings_dict)
    assert img is not None
    assert img.size == (1200, 630)


@pytest.mark.django_db
def test_generate_submission_preview_full_layout(event, submission):
    """Test generating a submission preview with full layout."""
    settings_dict = {"layout": "full", "show_event_logo": True}
    img = generate_submission_preview(event, submission, settings_dict)
    assert img is not None
    assert img.size == (1200, 630)


@pytest.mark.django_db
def test_generate_speaker_preview_default_layout(event, speaker):
    """Test generating a speaker preview with default layout."""
    img = generate_speaker_preview(event, speaker)
    assert img is not None
    assert img.size == (1200, 630)


@pytest.mark.django_db
def test_generate_speaker_preview_minimal_layout(event, speaker):
    """Test generating a speaker preview with minimal layout."""
    settings_dict = {"layout": "minimal", "show_event_name": True}
    img = generate_speaker_preview(event, speaker, settings_dict)
    assert img is not None
    assert img.size == (1200, 630)


@pytest.mark.django_db
def test_generate_speaker_preview_full_layout(event, speaker):
    """Test generating a speaker preview with full layout."""
    settings_dict = {"layout": "full", "show_avatar": True}
    img = generate_speaker_preview(event, speaker, settings_dict)
    assert img is not None
    assert img.size == (1200, 630)


@pytest.mark.django_db
def test_settings_hash_generation():
    """Test that settings hash is consistent and unique."""
    settings1 = {"layout": "default"}
    settings2 = {"layout": "default"}
    settings3 = {"layout": "minimal"}

    hash1 = get_settings_hash(settings1)
    hash2 = get_settings_hash(settings2)
    hash3 = get_settings_hash(settings3)

    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 8


@pytest.mark.django_db
def test_cache_submission_preview(event, submission):
    """Test caching of submission preview images."""
    settings_dict = event.social_preview_settings.get("submission", {})

    cached_before = get_cached_preview(event, "submission", submission.code, settings_dict)
    assert cached_before is None

    preview = generate_and_cache_submission_preview(event, submission)
    assert preview is not None

    cached_after = get_cached_preview(event, "submission", submission.code, settings_dict)
    assert cached_after is not None


@pytest.mark.django_db
def test_cache_speaker_preview(event, speaker):
    """Test caching of speaker preview images."""
    settings_dict = event.social_preview_settings.get("speaker", {})

    cached_before = get_cached_preview(event, "speaker", speaker.code, settings_dict)
    assert cached_before is None

    preview = generate_and_cache_speaker_preview(event, speaker)
    assert preview is not None

    cached_after = get_cached_preview(event, "speaker", speaker.code, settings_dict)
    assert cached_after is not None


@pytest.mark.django_db
def test_invalidate_submission_cache(event, submission):
    """Test invalidation of submission preview cache."""
    settings_dict = event.social_preview_settings.get("submission", {})

    preview = generate_and_cache_submission_preview(event, submission)
    assert preview is not None

    cached = get_cached_preview(event, "submission", submission.code, settings_dict)
    assert cached is not None

    invalidate_preview_cache(event, "submission", submission.code)

    cached_after = get_cached_preview(event, "submission", submission.code, settings_dict)
    assert cached_after is None


@pytest.mark.django_db
def test_invalidate_speaker_cache(event, speaker):
    """Test invalidation of speaker preview cache."""
    settings_dict = event.social_preview_settings.get("speaker", {})

    preview = generate_and_cache_speaker_preview(event, speaker)
    assert preview is not None

    cached = get_cached_preview(event, "speaker", speaker.code, settings_dict)
    assert cached is not None

    invalidate_preview_cache(event, "speaker", speaker.code)

    cached_after = get_cached_preview(event, "speaker", speaker.code, settings_dict)
    assert cached_after is None


@pytest.mark.django_db
def test_submission_update_invalidates_cache(event, submission):
    """Test that updating a submission invalidates its preview cache."""
    preview = generate_and_cache_submission_preview(event, submission)
    assert preview is not None

    settings_dict = event.social_preview_settings.get("submission", {})
    cached = get_cached_preview(event, "submission", submission.code, settings_dict)
    assert cached is not None

    submission.title = "Updated Title"
    submission.save()

    cached_after = get_cached_preview(event, "submission", submission.code, settings_dict)
    assert cached_after is None


@pytest.mark.django_db
def test_multiple_layouts_different_caches(event, submission):
    """Test that different layout settings result in different cache entries."""
    settings_default = {"layout": "default"}
    settings_minimal = {"layout": "minimal"}

    event.social_preview_settings["submission"] = settings_default
    event.save()
    preview_default = generate_and_cache_submission_preview(event, submission)
    assert preview_default is not None

    event.social_preview_settings["submission"] = settings_minimal
    event.save()

    cached_minimal = get_cached_preview(event, "submission", submission.code, settings_minimal)
    assert cached_minimal is None

    preview_minimal = generate_and_cache_submission_preview(event, submission)
    assert preview_minimal is not None

    cached_default = get_cached_preview(event, "submission", submission.code, settings_default)
    assert cached_default is not None


@pytest.mark.django_db
def test_error_handling_with_invalid_data(event, submission):
    """Test that image generation handles errors gracefully."""
    preview = generate_and_cache_submission_preview(event, submission)
    assert preview is not None


@pytest.mark.django_db
def test_generate_preview_with_missing_logo(event, submission):
    """Test that image generation works even when logo is missing."""
    event.logo = None
    event.save()
    img = generate_submission_preview(event, submission)
    assert img is not None
    assert img.size == (1200, 630)


@pytest.mark.django_db
def test_cached_preview_reused(event, submission):
    """Test that cached previews are reused."""
    preview1 = generate_and_cache_submission_preview(event, submission)
    preview2 = generate_and_cache_submission_preview(event, submission)

    assert preview1 is not None
    assert preview2 is not None
    assert preview1.tell() == preview2.tell()
