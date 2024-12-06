# Generated by Django 5.1.2 on 2024-10-25 07:17

import user.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Phone number must be in the format +639XXXXXXXXX', max_length=13, null=True, validators=[user.models.validate_phone_number]),
        ),
    ]
