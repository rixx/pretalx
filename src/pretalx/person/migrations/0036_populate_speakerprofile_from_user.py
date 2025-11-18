# Generated manually - Data migration for speaker names and avatars

from django.db import migrations


def populate_speakerprofile_from_user(apps, schema_editor):
    """
    Populate SpeakerProfile name and avatar fields from User model.

    This migration copies:
    - user.name to profile.name_parts as {"_legacy": user.name}
    - user.name to profile.name (cached display name)
    - user.avatar and thumbnails to profile (if user has them and profile doesn't)
    """
    SpeakerProfile = apps.get_model('person', 'SpeakerProfile')

    profiles = SpeakerProfile.objects.select_related('user').filter(user__isnull=False)

    profiles_to_update = []
    for profile in profiles:
        user = profile.user
        updated = False

        # Copy name from user if profile doesn't have name_parts
        if not profile.name_parts and user.name:
            profile.name_parts = {"_legacy": user.name}
            profile.name = user.name
            updated = True
        elif not profile.name and user.name:
            # Profile has name_parts but no cached name - set from user
            profile.name = user.name
            updated = True

        # Copy avatar from user to profile if user has it and profile doesn't
        if user.avatar and not profile.avatar:
            profile.avatar = user.avatar
            updated = True

        # Copy avatar thumbnails
        if user.avatar_thumbnail and not profile.avatar_thumbnail:
            profile.avatar_thumbnail = user.avatar_thumbnail
            updated = True

        if user.avatar_thumbnail_tiny and not profile.avatar_thumbnail_tiny:
            profile.avatar_thumbnail_tiny = user.avatar_thumbnail_tiny
            updated = True

        if updated:
            profiles_to_update.append(profile)

    # Bulk update for efficiency
    if profiles_to_update:
        SpeakerProfile.objects.bulk_update(
            profiles_to_update,
            ['name_parts', 'name', 'avatar', 'avatar_thumbnail', 'avatar_thumbnail_tiny'],
            batch_size=500
        )


def reverse_populate(apps, schema_editor):
    """
    Reverse the migration by clearing the populated fields.

    Note: This doesn't restore original data, just clears what was populated.
    """
    SpeakerProfile = apps.get_model('person', 'SpeakerProfile')

    # Only clear profiles that have _legacy name_parts (i.e., migrated from user)
    profiles = SpeakerProfile.objects.filter(name_parts__has_key='_legacy')

    for profile in profiles:
        profile.name_parts = {}
        profile.name = ""

    SpeakerProfile.objects.bulk_update(
        list(profiles),
        ['name_parts', 'name'],
        batch_size=500
    )


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0035_add_name_parts_to_speakerprofile'),
    ]

    operations = [
        migrations.RunPython(
            populate_speakerprofile_from_user,
            reverse_populate,
        ),
    ]
