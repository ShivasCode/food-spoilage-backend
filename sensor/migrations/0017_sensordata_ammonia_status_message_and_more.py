# Generated by Django 5.1.2 on 2024-12-04 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0016_alter_sensordata_food_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensordata',
            name='ammonia_status_message',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='monitoringgroup',
            name='food_type',
            field=models.CharField(choices=[('menudo', 'Menudo'), ('adobo', 'Adobo'), ('mechado', 'Mechado'), ('general', 'General'), ('bicol express', 'Bicol Express')], max_length=50),
        ),
    ]