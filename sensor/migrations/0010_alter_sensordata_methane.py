# Generated by Django 5.1.2 on 2024-11-27 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0009_alter_sensordata_threshold'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensordata',
            name='methane',
            field=models.FloatField(),
        ),
    ]