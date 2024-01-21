# Generated by Django 5.0.1 on 2024-01-21 18:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_is_verified_otp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]