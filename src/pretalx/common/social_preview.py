# SPDX-FileCopyrightText: 2024-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

import hashlib
import os
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image, ImageDraw, ImageFont


# Social media image dimensions (optimized for Twitter/OG)
PREVIEW_WIDTH = 1200
PREVIEW_HEIGHT = 630

# Color defaults
DEFAULT_BG_COLOR = "#ffffff"
DEFAULT_TEXT_COLOR = "#000000"
DEFAULT_ACCENT_COLOR = "#1da1f2"


def get_font(size, bold=False):
    """Get a font with fallback to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    return ImageFont.load_default()


def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def load_and_resize_image(image_file, max_size):
    """Load an image and resize it to fit within max_size while maintaining aspect ratio."""
    if not image_file:
        return None

    try:
        if hasattr(image_file, 'path'):
            img = Image.open(image_file.path)
        else:
            img = Image.open(image_file)

        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA')

        return img
    except Exception:
        return None


def create_circular_mask(size):
    """Create a circular mask for avatar images."""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    return mask


def generate_submission_preview(event, submission, settings_dict=None):
    """Generate a social preview image for a submission."""
    if not settings_dict:
        settings_dict = event.social_preview_settings.get("submission", {})

    if not settings_dict.get("enabled", True):
        return None

    layout = settings_dict.get("layout", "default")

    if layout == "minimal":
        return _generate_minimal_submission(event, submission, settings_dict)
    elif layout == "full":
        return _generate_full_submission(event, submission, settings_dict)
    else:
        return _generate_default_submission(event, submission, settings_dict)


def generate_speaker_preview(event, speaker, settings_dict=None):
    """Generate a social preview image for a speaker."""
    if not settings_dict:
        settings_dict = event.social_preview_settings.get("speaker", {})

    if not settings_dict.get("enabled", True):
        return None

    layout = settings_dict.get("layout", "default")

    if layout == "minimal":
        return _generate_minimal_speaker(event, speaker, settings_dict)
    elif layout == "full":
        return _generate_full_speaker(event, speaker, settings_dict)
    else:
        return _generate_default_speaker(event, speaker, settings_dict)


def _generate_default_submission(event, submission, settings_dict):
    """Generate default layout for submission preview."""
    img = Image.new('RGB', (PREVIEW_WIDTH, PREVIEW_HEIGHT), color=DEFAULT_BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Colors
    bg_color = DEFAULT_BG_COLOR
    text_color = DEFAULT_TEXT_COLOR
    accent_color = event.primary_color or DEFAULT_ACCENT_COLOR

    # Add colored accent bar at top
    draw.rectangle([(0, 0), (PREVIEW_WIDTH, 10)], fill=accent_color)

    y_offset = 60
    padding = 60

    # Add event logo if enabled
    if settings_dict.get("show_event_logo", True) and event.logo:
        logo = load_and_resize_image(event.logo, (200, 100))
        if logo:
            logo_x = padding
            img.paste(logo, (logo_x, y_offset), logo if logo.mode == 'RGBA' else None)
            y_offset += logo.height + 40

    # Add event name if enabled
    if settings_dict.get("show_event_name", True):
        font_event = get_font(32, bold=True)
        event_name = str(event.name)
        draw.text((padding, y_offset), event_name, fill=accent_color, font=font_event)
        y_offset += 60

    # Add submission title
    font_title = get_font(56, bold=True)
    max_text_width = PREVIEW_WIDTH - (2 * padding)
    title_lines = wrap_text(str(submission.title), font_title, max_text_width)

    for line in title_lines[:3]:
        draw.text((padding, y_offset), line, fill=text_color, font=font_title)
        y_offset += 70

    # Add speaker names if enabled
    if settings_dict.get("show_speaker_avatars", True):
        y_offset += 20
        speakers = submission.speakers.all()[:3]

        if speakers:
            font_speaker = get_font(28)
            speaker_names = ", ".join([str(s.name) for s in speakers])
            speaker_lines = wrap_text(speaker_names, font_speaker, max_text_width)

            for line in speaker_lines[:2]:
                draw.text((padding, y_offset), line, fill=text_color, font=font_speaker)
                y_offset += 40

    return img


def _generate_minimal_submission(event, submission, settings_dict):
    """Generate minimal layout for submission preview."""
    img = Image.new('RGB', (PREVIEW_WIDTH, PREVIEW_HEIGHT), color=DEFAULT_BG_COLOR)
    draw = ImageDraw.Draw(img)

    accent_color = event.primary_color or DEFAULT_ACCENT_COLOR
    text_color = DEFAULT_TEXT_COLOR

    # Simple centered design
    padding = 100

    # Title in the center
    font_title = get_font(64, bold=True)
    max_text_width = PREVIEW_WIDTH - (2 * padding)
    title_lines = wrap_text(str(submission.title), font_title, max_text_width)

    total_height = len(title_lines) * 80
    y_offset = (PREVIEW_HEIGHT - total_height) // 2

    for line in title_lines[:4]:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        text_width = bbox[2] - bbox[0]
        x = (PREVIEW_WIDTH - text_width) // 2
        draw.text((x, y_offset), line, fill=text_color, font=font_title)
        y_offset += 80

    # Small event name at bottom
    if settings_dict.get("show_event_name", True):
        font_event = get_font(24)
        event_text = str(event.name)
        bbox = draw.textbbox((0, 0), event_text, font=font_event)
        text_width = bbox[2] - bbox[0]
        x = (PREVIEW_WIDTH - text_width) // 2
        draw.text((x, PREVIEW_HEIGHT - 60), event_text, fill=accent_color, font=font_event)

    return img


def _generate_full_submission(event, submission, settings_dict):
    """Generate full layout for submission preview with all elements."""
    img = Image.new('RGB', (PREVIEW_WIDTH, PREVIEW_HEIGHT), color=DEFAULT_BG_COLOR)
    draw = ImageDraw.Draw(img)

    accent_color = event.primary_color or DEFAULT_ACCENT_COLOR
    text_color = DEFAULT_TEXT_COLOR

    # Left column for branding and speakers
    left_width = 400
    padding = 40

    # Draw vertical divider
    draw.rectangle([(left_width, 0), (left_width + 4, PREVIEW_HEIGHT)], fill=accent_color)

    # Left column content
    y_left = padding

    # Event logo
    if settings_dict.get("show_event_logo", True) and event.logo:
        logo = load_and_resize_image(event.logo, (left_width - 2 * padding, 150))
        if logo:
            logo_x = (left_width - logo.width) // 2
            img.paste(logo, (logo_x, y_left), logo if logo.mode == 'RGBA' else None)
            y_left += logo.height + 30

    # Event name
    if settings_dict.get("show_event_name", True):
        font_event = get_font(28, bold=True)
        event_lines = wrap_text(str(event.name), font_event, left_width - 2 * padding)
        for line in event_lines[:2]:
            bbox = draw.textbbox((0, 0), line, font=font_event)
            text_width = bbox[2] - bbox[0]
            x = (left_width - text_width) // 2
            draw.text((x, y_left), line, fill=accent_color, font=font_event)
            y_left += 36

    # Speaker avatars
    if settings_dict.get("show_speaker_avatars", True):
        y_left += 40
        speakers = submission.speakers.all()[:2]

        for speaker in speakers:
            if hasattr(speaker, 'event_profile'):
                try:
                    profile = speaker.event_profile(event)
                    if profile and profile.avatar:
                        avatar = load_and_resize_image(profile.avatar, (100, 100))
                        if avatar:
                            mask = create_circular_mask((100, 100))
                            avatar_x = (left_width - 100) // 2

                            if avatar.mode == 'RGBA':
                                img.paste(avatar, (avatar_x, y_left), mask)
                            else:
                                avatar_rgb = avatar.convert('RGB')
                                img.paste(avatar_rgb, (avatar_x, y_left), mask)

                            y_left += 110

                            font_name = get_font(20)
                            name_lines = wrap_text(str(speaker.name), font_name, left_width - 2 * padding)
                            for line in name_lines[:2]:
                                bbox = draw.textbbox((0, 0), line, font=font_name)
                                text_width = bbox[2] - bbox[0]
                                x = (left_width - text_width) // 2
                                draw.text((x, y_left), line, fill=text_color, font=font_name)
                                y_left += 28

                            y_left += 20
                except Exception:
                    pass

    # Right column - submission title
    right_x = left_width + 40
    right_width = PREVIEW_WIDTH - left_width - 80
    y_right = 100

    font_title = get_font(52, bold=True)
    title_lines = wrap_text(str(submission.title), font_title, right_width)

    for line in title_lines[:4]:
        draw.text((right_x, y_right), line, fill=text_color, font=font_title)
        y_right += 65

    # Submission type/track
    y_right += 20
    font_meta = get_font(24)
    meta_parts = []

    if submission.submission_type:
        meta_parts.append(str(submission.submission_type.name))
    if submission.track:
        meta_parts.append(str(submission.track.name))

    if meta_parts:
        meta_text = " • ".join(meta_parts)
        draw.text((right_x, y_right), meta_text, fill=accent_color, font=font_meta)

    return img


def _generate_default_speaker(event, speaker, settings_dict):
    """Generate default layout for speaker preview."""
    img = Image.new('RGB', (PREVIEW_WIDTH, PREVIEW_HEIGHT), color=DEFAULT_BG_COLOR)
    draw = ImageDraw.Draw(img)

    accent_color = event.primary_color or DEFAULT_ACCENT_COLOR
    text_color = DEFAULT_TEXT_COLOR

    draw.rectangle([(0, 0), (PREVIEW_WIDTH, 10)], fill=accent_color)

    y_offset = 60
    padding = 60

    # Add event logo
    if settings_dict.get("show_event_logo", True) and event.logo:
        logo = load_and_resize_image(event.logo, (200, 100))
        if logo:
            img.paste(logo, (padding, y_offset), logo if logo.mode == 'RGBA' else None)
            y_offset += logo.height + 40

    # Add event name
    if settings_dict.get("show_event_name", True):
        font_event = get_font(32, bold=True)
        draw.text((padding, y_offset), str(event.name), fill=accent_color, font=font_event)
        y_offset += 60

    # Speaker avatar
    if settings_dict.get("show_avatar", True):
        try:
            if hasattr(speaker, 'event_profile'):
                profile = speaker.event_profile(event)
                if profile and profile.avatar:
                    avatar = load_and_resize_image(profile.avatar, (250, 250))
                    if avatar:
                        mask = create_circular_mask((250, 250))
                        avatar_x = padding

                        if avatar.mode == 'RGBA':
                            img.paste(avatar, (avatar_x, y_offset), mask)
                        else:
                            avatar_rgb = avatar.convert('RGB')
                            img.paste(avatar_rgb, (avatar_x, y_offset), mask)

                        y_offset = 60
                        padding = padding + 250 + 60
        except Exception:
            pass

    # Speaker name
    font_name = get_font(64, bold=True)
    max_text_width = PREVIEW_WIDTH - (2 * padding)
    name_lines = wrap_text(str(speaker.name), font_name, max_text_width)

    for line in name_lines[:2]:
        draw.text((padding, y_offset), line, fill=text_color, font=font_name)
        y_offset += 75

    return img


def _generate_minimal_speaker(event, speaker, settings_dict):
    """Generate minimal layout for speaker preview."""
    img = Image.new('RGB', (PREVIEW_WIDTH, PREVIEW_HEIGHT), color=DEFAULT_BG_COLOR)
    draw = ImageDraw.Draw(img)

    accent_color = event.primary_color or DEFAULT_ACCENT_COLOR
    text_color = DEFAULT_TEXT_COLOR

    # Centered speaker name
    font_name = get_font(72, bold=True)
    speaker_name = str(speaker.name)
    bbox = draw.textbbox((0, 0), speaker_name, font=font_name)
    text_width = bbox[2] - bbox[0]

    x = (PREVIEW_WIDTH - text_width) // 2
    y = (PREVIEW_HEIGHT - 100) // 2

    draw.text((x, y), speaker_name, fill=text_color, font=font_name)

    # Event name at bottom
    if settings_dict.get("show_event_name", True):
        font_event = get_font(24)
        event_text = str(event.name)
        bbox = draw.textbbox((0, 0), event_text, font=font_event)
        text_width = bbox[2] - bbox[0]
        x = (PREVIEW_WIDTH - text_width) // 2
        draw.text((x, PREVIEW_HEIGHT - 60), event_text, fill=accent_color, font=font_event)

    return img


def _generate_full_speaker(event, speaker, settings_dict):
    """Generate full layout for speaker preview."""
    return _generate_default_speaker(event, speaker, settings_dict)


def get_preview_cache_path(event, object_type, object_id, settings_hash):
    """Get the cache path for a preview image."""
    filename = f"{object_type}_{object_id}_{settings_hash}.png"
    return os.path.join(
        "social_previews",
        event.slug,
        filename
    )


def get_settings_hash(settings_dict):
    """Generate a hash from settings dict to use in cache key."""
    settings_str = str(sorted(settings_dict.items()))
    return hashlib.md5(settings_str.encode()).hexdigest()[:8]


def get_cached_preview(event, object_type, object_id, settings_dict):
    """Retrieve a cached preview image if it exists."""
    settings_hash = get_settings_hash(settings_dict)
    cache_path = get_preview_cache_path(event, object_type, object_id, settings_hash)

    if default_storage.exists(cache_path):
        try:
            with default_storage.open(cache_path, 'rb') as f:
                return BytesIO(f.read())
        except Exception:
            pass

    return None


def save_preview_to_cache(img, event, object_type, object_id, settings_dict):
    """Save a generated preview image to cache."""
    if not img:
        return None

    settings_hash = get_settings_hash(settings_dict)
    cache_path = get_preview_cache_path(event, object_type, object_id, settings_hash)

    buffer = BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    buffer.seek(0)

    try:
        default_storage.save(cache_path, buffer)
        buffer.seek(0)
        return buffer
    except Exception:
        buffer.seek(0)
        return buffer


def invalidate_preview_cache(event, object_type, object_id):
    """Invalidate all cached preview images for a specific object."""
    cache_dir = os.path.join("social_previews", event.slug)

    if not default_storage.exists(cache_dir):
        return

    try:
        dirs, files = default_storage.listdir(cache_dir)
        prefix = f"{object_type}_{object_id}_"

        for filename in files:
            if filename.startswith(prefix):
                file_path = os.path.join(cache_dir, filename)
                default_storage.delete(file_path)
    except Exception:
        pass


def generate_and_cache_submission_preview(event, submission):
    """Generate and cache a submission preview image."""
    settings_dict = event.social_preview_settings.get("submission", {})

    if not settings_dict.get("enabled", True):
        return None

    cached = get_cached_preview(event, "submission", submission.code, settings_dict)
    if cached:
        return cached

    img = generate_submission_preview(event, submission, settings_dict)
    if img:
        return save_preview_to_cache(img, event, "submission", submission.code, settings_dict)

    return None


def generate_and_cache_speaker_preview(event, speaker):
    """Generate and cache a speaker preview image."""
    settings_dict = event.social_preview_settings.get("speaker", {})

    if not settings_dict.get("enabled", True):
        return None

    cached = get_cached_preview(event, "speaker", speaker.code, settings_dict)
    if cached:
        return cached

    img = generate_speaker_preview(event, speaker, settings_dict)
    if img:
        return save_preview_to_cache(img, event, "speaker", speaker.code, settings_dict)

    return None
