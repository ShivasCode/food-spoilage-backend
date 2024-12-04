import pandas as pd
import plotly.express as px
from django.core.management.base import BaseCommand
from sensor.models import SensorData

class Command(BaseCommand):
    help = "Generate a methane graph for monitoring group ID 604"

    def handle(self, *args, **kwargs):
        # Monitoring group ID
        monitoring_group_id = 604
        interval_seconds = 300  # 5-minute intervals

        # Fetch and process data
        self.stdout.write("Fetching sensor data...")
        df = self.fetch_data(monitoring_group_id, interval_seconds)

        if df.empty:
            self.stdout.write(self.style.WARNING(f"No data found for monitoring group ID {monitoring_group_id}."))
            return

        # Generate the plot
        self.stdout.write("Generating plot...")
        self.plot_methane_data(df)
        self.stdout.write(self.style.SUCCESS("Plot generated successfully."))

    def fetch_data(self, monitoring_group_id, interval_seconds):
        # Query SensorData for the given monitoring group ID
        sensor_data = SensorData.objects.filter(monitoring_group_id=monitoring_group_id).values('timestamp', 'methane')

        # Convert the data to a Pandas DataFrame
        df = pd.DataFrame.from_records(sensor_data)

        # Ensure timestamp is in datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Round timestamps to the nearest interval
        df['timestamp'] = df['timestamp'].dt.floor(f'{interval_seconds // 60}T')

        return df

    def plot_methane_data(self, df):
        # Create a line plot using Plotly
        fig = px.line(
            df,
            x='timestamp',
            y='methane',
            title='Methane Levels for Monitoring Group ID 604 (5-Minute Intervals)',
            labels={'timestamp': 'Timestamp', 'methane': 'Methane Levels (ppm)'},
        )

        # Update layout for better readability
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Methane Levels (ppm)',
            template='plotly_dark'
        )

        # Show the plot in the default browser
        fig.show()
