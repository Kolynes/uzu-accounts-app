# Generated by Django 3.0.7 on 2020-12-08 11:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('AccountsApp', '0002_auto_20201208_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twofactortokens',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
