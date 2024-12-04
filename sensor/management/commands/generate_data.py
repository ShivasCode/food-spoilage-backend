import csv
from django.core.management.base import BaseCommand
from sensor.models import SensorData  # Replace 'sensor' with the name of your app
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate CSV files of SensorData at different intervals (timestamp and methane only)'

    def handle(self, *args, **kwargs):
        # Define the monitoring group ID
        monitoring_group_id = 604

        # Query SensorData for the specific monitoring group ID
        sensor_data = SensorData.objects.filter(monitoring_group_id=monitoring_group_id).order_by('timestamp')

        # Check if there is any data
        if not sensor_data.exists():
            self.stdout.write(self.style.WARNING(f'No data found for monitoring group ID {monitoring_group_id}'))
            return

        # Define intervals in seconds
        intervals = {
            '10_seconds': 10,
            '1_minute': 60,
            '3_minutes': 180,
            '5_minutes': 300,
        }

        # Iterate through each interval
        for interval_name, interval_seconds in intervals.items():
            self.generate_csv(sensor_data, interval_name, interval_seconds, monitoring_group_id)

    def generate_csv(self, sensor_data, interval_name, interval_seconds, monitoring_group_id):
        # Define the file name with current timestamp and interval
        filename = f"sensor_data_{interval_name}_group_{monitoring_group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Open the CSV file
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'methane']  # Only include timestamp and methane

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header row
            writer.writeheader()

            # Write data rows at the specified interval
            last_timestamp = None
            for data in sensor_data:
                if not last_timestamp or (data.timestamp - last_timestamp).total_seconds() >= interval_seconds:
                    writer.writerow({
                        'timestamp': data.timestamp,
                        'methane': data.methane,
                    })
                    last_timestamp = data.timestamp

        # Provide feedback
        self.stdout.write(self.style.SUCCESS(f'Generated CSV for {interval_name}: {filename}'))
