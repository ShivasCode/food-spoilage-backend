# Generated by Django 5.1.2 on 2024-11-26 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0008_sensordata_ammonia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensordata',
            name='threshold',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]