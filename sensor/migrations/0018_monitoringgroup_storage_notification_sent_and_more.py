# Generated by Django 5.1.2 on 2024-12-04 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0017_sensordata_ammonia_status_message_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitoringgroup',
            name='storage_notification_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monitoringgroup',
            name='temperature_notification_sent',
            field=models.BooleanField(default=False),
        ),
    ]