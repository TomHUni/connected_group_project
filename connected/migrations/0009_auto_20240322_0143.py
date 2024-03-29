# Generated by Django 2.2.28 on 2024-03-22 01:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('connected', '0008_friendship'),
    ]

    operations = [
        migrations.AddField(
            model_name='tab',
            name='friday_schedule',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tab',
            name='monday_schedule',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tab',
            name='saturday_schedule',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tab',
            name='sunday_schedule',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tab',
            name='thursday_schedule',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tab',
            name='tuesday_schedule',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tab',
            name='wednesday_schedule',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='friends',
            field=models.ManyToManyField(blank=True, related_name='_userprofile_friends_+', to='connected.UserProfile'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
