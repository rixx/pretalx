# Generated migration for adding is_blocker field to TalkSlot

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0017_created_updated_everywhere'),
    ]

    operations = [
        migrations.AddField(
            model_name='talkslot',
            name='is_blocker',
            field=models.BooleanField(default=False, help_text='Blocker sessions are not visible in the public schedule'),
        ),
    ]
