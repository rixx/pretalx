# Generated manually

from django.db import migrations, models
import django.db.models.deletion
from django_scopes import ScopedManager


def migrate_speaker_roles_to_profiles(apps, schema_editor):
    """Migrate SpeakerRole from User to SpeakerProfile.

    For each SpeakerRole:
    1. Get or create a SpeakerProfile for the user+event combination
    2. Link the SpeakerRole to that SpeakerProfile
    """
    SpeakerRole = apps.get_model('submission', 'SpeakerRole')
    SpeakerProfile = apps.get_model('person', 'SpeakerProfile')

    for role in SpeakerRole.objects.all():
        if not role.user:
            # Skip roles without a user (shouldn't happen, but be safe)
            continue

        # Get or create SpeakerProfile for this user+event combination
        event = role.submission.event
        profile, created = SpeakerProfile.objects.get_or_create(
            user=role.user,
            event=event
        )

        # Link the SpeakerRole to the profile
        role.speaker_profile = profile
        role.save(update_fields=['speaker_profile'])


def reverse_migration(apps, schema_editor):
    """Reverse the migration by copying speaker_profile.user back to user field."""
    SpeakerRole = apps.get_model('submission', 'SpeakerRole')

    for role in SpeakerRole.objects.all():
        if role.speaker_profile:
            role.user = role.speaker_profile.user
            role.save(update_fields=['user'])


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0086_alter_question_icon'),
        ('person', '0032_speakerprofile_internal_notes'),
    ]

    operations = [
        # Step 1: Add speaker_profile field as nullable
        migrations.AddField(
            model_name='speakerrole',
            name='speaker_profile',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='speaker_roles',
                to='person.speakerprofile'
            ),
        ),

        # Step 2: Migrate data from user to speaker_profile
        migrations.RunPython(
            migrate_speaker_roles_to_profiles,
            reverse_migration
        ),

        # Step 3: Make speaker_profile non-nullable
        migrations.AlterField(
            model_name='speakerrole',
            name='speaker_profile',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='speaker_roles',
                to='person.speakerprofile'
            ),
        ),

        # Step 4: Remove the old unique_together constraint on (submission, user)
        migrations.AlterUniqueTogether(
            name='speakerrole',
            unique_together=set(),
        ),

        # Step 5: Add new unique_together constraint on (submission, speaker_profile)
        migrations.AlterUniqueTogether(
            name='speakerrole',
            unique_together={('submission', 'speaker_profile')},
        ),

        # Step 6: Remove the old user field
        migrations.RemoveField(
            model_name='speakerrole',
            name='user',
        ),

        # Step 7: Rename speakers to speaker_profiles in Submission
        migrations.RenameField(
            model_name='submission',
            old_name='speakers',
            new_name='speaker_profiles',
        ),

        # Step 8: Update the through model reference
        migrations.AlterField(
            model_name='submission',
            name='speaker_profiles',
            field=models.ManyToManyField(
                blank=True,
                related_name='submissions',
                through='submission.SpeakerRole',
                to='person.speakerprofile',
                verbose_name='Speakers'
            ),
        ),
    ]
