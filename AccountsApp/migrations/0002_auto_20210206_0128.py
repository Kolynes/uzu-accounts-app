# Generated by Django 2.0.6 on 2021-02-06 01:28

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('AccountsApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Verification',
            new_name='VerificationModel',
        ),
    ]