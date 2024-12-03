from django.core.management.base import BaseCommand
from datetime import timedelta
from sensor.models import MonitoringGroup, SensorData
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generates sensor data for a given MonitoringGroup'

    def handle(self, *args, **kwargs):
        # Retrieve the MonitoringGroup object
        monitoring_group = MonitoringGroup.objects.get(id=517)

        # Start and end times for the simulation
        start_time = monitoring_group.start_time
        end_time = monitoring_group.end_time if monitoring_group.end_time else timezone.now()

        # Initial values for the sensor data
        temperature_range = (29, 31)  # Unused as methane will trigger spoilage
        humidity_range = (60, 75)  # Unused as methane will trigger spoilage
        methane_max = 30
        ammonia_range = (0.1, 0.5)

        # Initialize methane value and spoilage flag
        methane = 0
        spoilage_triggered = False
        current_time = start_time

        # Simulate sensor data every 10 seconds between the start and end time
        while current_time <= end_time:
            # Gradually increase methane value until it reaches the max limit
            methane = min(methane + random.uniform(0.1, 0.2), methane_max)
            # Ensure methane has at most 2 decimal places
            methane = round(methane, 2)

            # Generate random values for temperature, humidity, and ammonia, all rounded to 2 decimals
            temperature = round(random.uniform(*temperature_range), 2)
            humidity = round(random.uniform(*humidity_range), 2)
            ammonia = round(random.uniform(*ammonia_range), 2)

            # Determine spoilage status based only on methane
            if methane >= 20:
                spoilage_status = 'food_is_spoiled'
                spoilage_triggered = True
            else:
                spoilage_status = 'food_is_fresh'

            # Create a SensorData object
            SensorData.objects.create(
                user=monitoring_group.user,
                monitoring_group=monitoring_group,
                temperature=temperature,
                humidity=humidity,
                methane=methane,
                ammonia=ammonia,
                spoilage_status=spoilage_status,
                timestamp=current_time,
                food_type=monitoring_group.food_type
            )

            # If spoilage is triggered, end the monitoring group and break the loop
            if spoilage_triggered:
                monitoring_group.is_done = True
                monitoring_group.end_time = current_time
                monitoring_group.save()
                self.stdout.write(self.style.SUCCESS(f"Monitoring ended at {current_time}. Food is spoiled."))
                break

            # Increment the time by 10 seconds
            current_time += timedelta(seconds=10)

        self.stdout.write(self.style.SUCCESS("Sensor data created successfully."))
