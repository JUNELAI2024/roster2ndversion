# Generated by Django 5.1.4 on 2025-03-30 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0008_dailyrevenue'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailyrevenue',
            name='user',
        ),
        migrations.AddField(
            model_name='dailyrevenue',
            name='user_input',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
