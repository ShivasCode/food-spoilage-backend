# Generated by Django 5.1.2 on 2024-10-24 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0003_sensordata_food_type_monitoringgroup_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensordata',
            name='spoilage_status',
            field=models.CharField(choices=[('food_is_fresh', 'Food is Fresh'), ('food_is_at_risk', 'Food is at Risk'), ('food_is_spoiled', 'Food is Spoiled')], default='food_is_fresh', max_length=50),
        ),
    ]
