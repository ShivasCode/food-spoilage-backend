# Generated by Django 5.1.2 on 2024-11-29 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0010_alter_sensordata_methane'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensordata',
            name='reason_of_spoilage',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]