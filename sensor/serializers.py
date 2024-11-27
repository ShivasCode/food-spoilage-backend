from rest_framework import serializers
from sensor.models import MonitoringGroup, SensorData, Notification
from django.utils import timezone

class SensorDataSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format="%m/%d/%y %I:%M%p", default_timezone=timezone.get_current_timezone())

    class Meta:
        model = SensorData
        fields = ['id', 'temperature', 'humidity', 'methane', 'ammonia','threshold', 'timestamp', 'food_type', 'spoilage_status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Format the timestamp to a more human-friendly format (local time zone)
        representation['timestamp'] = timezone.localtime(instance.timestamp).strftime("%m/%d/%y %I:%M%p")
        return representation

class MonitoringGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoringGroup
        fields = ['id', 'food_type', 'start_time', 'end_time', 'is_done']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Format start_time and end_time to a more human-friendly format in local time zone
        representation['start_time'] = timezone.localtime(instance.start_time).strftime("%B %d, %Y, %I:%M %p") if instance.start_time else None
        representation['end_time'] = timezone.localtime(instance.end_time).strftime("%B %d, %Y, %I:%M %p") if instance.end_time else None
        return representation

class SensorDataFormattedSerializer(serializers.ModelSerializer):
    formatted_timestamp = serializers.SerializerMethodField()
    spoilage_status = serializers.SerializerMethodField()

    class Meta:
        model = SensorData
        fields = [
            'id', 'temperature', 'humidity', 'methane', 'ammonia','threshold', 
            'formatted_timestamp', 'food_type', 'spoilage_status'
        ]

    def get_formatted_timestamp(self, obj):
        # Convert timestamp to the local time zone before formatting
        timestamp = timezone.localtime(obj.timestamp)
        return timestamp.strftime("%m/%d/%y %I:%M%p") if timestamp else None

    def get_spoilage_status(self, obj):
        # Get the human-readable value of the spoilage_status field
        return dict(SensorData.SPOILAGE_STATUS_CHOICES).get(obj.spoilage_status, obj.spoilage_status)

class MonitoringGroupDetailSerializer(serializers.ModelSerializer):
    sensor_data = serializers.SerializerMethodField()

    class Meta:
        model = MonitoringGroup
        fields = ['id', 'food_type', 'start_time', 'end_time', 'is_done', 'sensor_data']

    def get_sensor_data(self, obj):
        # Get sensor data associated with the monitoring group, ordered from latest to oldest
        sensor_data = obj.sensor_data.order_by('-timestamp')  # Latest first
        # Serialize sensor data and format timestamps
        return SensorDataFormattedSerializer(sensor_data, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert start_time and end_time to the local time zone and format them
        representation['start_time'] = timezone.localtime(instance.start_time).strftime("%m/%d/%y %I:%M%p") if instance.start_time else None
        representation['end_time'] = timezone.localtime(instance.end_time).strftime("%m/%d/%y %I:%M%p") if instance.end_time else None

        return representation


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'monitoring_group', 'message', 'timestamp', 'read']