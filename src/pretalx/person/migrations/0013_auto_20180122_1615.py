# Generated by Django 2.0.1 on 2018-01-22 22:15

from django.db import migrations


def create_administrators(apps, schema_editor):
    User = apps.get_model("person", "User")
    User.objects.filter(is_superuser=True).update(is_superuser=False, is_administrator=True)


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0012_user_is_administrator'),
    ]

    operations = [
        migrations.RunPython(create_administrators, migrations.RunPython.noop),
    ]
