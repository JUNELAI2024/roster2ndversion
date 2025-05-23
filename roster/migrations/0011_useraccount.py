# Generated by Django 5.1.4 on 2025-03-31 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0010_dailyrevenue_total_sum'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('username', models.CharField(max_length=150, unique=True)),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128)),
                ('create_date', models.DateField(auto_now_add=True)),
                ('create_time', models.TimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1)),
            ],
        ),
    ]
