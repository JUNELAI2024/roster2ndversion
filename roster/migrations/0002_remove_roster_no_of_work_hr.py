# Generated by Django 5.1.4 on 2025-02-03 02:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roster',
            name='no_of_work_hr',
        ),
    ]
