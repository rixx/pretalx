# Generated manually

from django.db import migrations, models
import pretalx.person.models.profile


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0033_usereventpreferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='speakerprofile',
            name='avatar',
            field=models.ImageField(
                blank=True,
                help_text='Event-specific profile picture. Falls back to your global profile picture if not set.',
                null=True,
                upload_to=pretalx.person.models.profile.speaker_avatar_path,
                verbose_name='Profile picture'
            ),
        ),
        migrations.AddField(
            model_name='speakerprofile',
            name='avatar_thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
        migrations.AddField(
            model_name='speakerprofile',
            name='avatar_thumbnail_tiny',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]
