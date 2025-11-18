# Generated manually

from django.db import migrations, models
import django.db.models.deletion


def migrate_answer_person_to_speaker_profile(apps, schema_editor):
    """Migrate Answer.person to Answer.speaker_profile.

    For each Answer with a person:
    1. Get or create a SpeakerProfile for the person+event combination
    2. Link the Answer to that SpeakerProfile
    """
    Answer = apps.get_model('submission', 'Answer')
    SpeakerProfile = apps.get_model('person', 'SpeakerProfile')

    for answer in Answer.objects.filter(person__isnull=False):
        event = answer.question.event

        # Get or create SpeakerProfile for this user+event combination
        profile, created = SpeakerProfile.objects.get_or_create(
            user=answer.person,
            event=event
        )

        # Link the Answer to the profile
        answer.speaker_profile = profile
        answer.save(update_fields=['speaker_profile'])


def reverse_migration(apps, schema_editor):
    """Reverse the migration by copying speaker_profile.user back to person field."""
    Answer = apps.get_model('submission', 'Answer')

    for answer in Answer.objects.filter(speaker_profile__isnull=False):
        answer.person = answer.speaker_profile.user
        answer.save(update_fields=['person'])


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0087_speaker_profile_migration'),
        ('person', '0033_usereventpreferences'),
    ]

    operations = [
        # Step 1: Add speaker_profile field as nullable
        migrations.AddField(
            model_name='answer',
            name='speaker_profile',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='answers',
                to='person.speakerprofile'
            ),
        ),

        # Step 2: Migrate data from person to speaker_profile
        migrations.RunPython(
            migrate_answer_person_to_speaker_profile,
            reverse_migration
        ),

        # Step 3: Remove the old person field
        migrations.RemoveField(
            model_name='answer',
            name='person',
        ),
    ]
