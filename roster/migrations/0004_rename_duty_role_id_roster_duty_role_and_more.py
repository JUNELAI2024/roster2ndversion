# Generated by Django 5.1.4 on 2025-02-03 01:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0003_remove_roster_duty_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='roster',
            old_name='duty_role_id',
            new_name='duty_role',
        ),
        migrations.RemoveField(
            model_name='roster',
            name='no_of_work_hr',
        ),
    ]
