from django.db import models
from user.models import CustomUser
# Create your models here.
from django.utils import timezone







class MonitoringGroup(models.Model):
    FOOD_CHOICES = [
        ('menudo', 'Menudo'),
        ('adobo', 'Adobo'),
        ('mechado', 'Mechado'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='monitoring_groups')
    food_type = models.CharField(max_length=50, choices=FOOD_CHOICES)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    email_notification_sent = models.BooleanField(default=False)  
    phone_notification_sent = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.food_type} monitoring for {self.user.username} | id: {self.id}"

class SensorData(models.Model):
    FOOD_CHOICES = [
        ('menudo', 'Menudo'),
        ('adobo', 'Adobo'),
        ('mechado', 'Mechado'),
    ]

    SPOILAGE_STATUS_CHOICES = [
        ('food_is_fresh', 'Food is Fresh'),
        ('food_is_at_risk', 'Food is at Risk'),
        ('food_is_spoiled', 'Food is Spoiled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_sensor', null=True)
    monitoring_group = models.ForeignKey(MonitoringGroup, on_delete=models.CASCADE, related_name='sensor_data', null=True)
    temperature = models.FloatField()
    humidity = models.FloatField()
    methane = models.FloatField()
    ammonia = models.FloatField()
    threshold = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField()
    food_type = models.CharField(max_length=50, choices=FOOD_CHOICES, null=True)
    spoilage_status = models.CharField(max_length=50, choices=SPOILAGE_STATUS_CHOICES, default='food_is_fresh')
    
    def __str__(self):
        # Access the monitoring group associated with this sensor data
        if self.monitoring_group:
            group_id = self.monitoring_group.id
            start_time = self.monitoring_group.start_time
            end_time = self.monitoring_group.end_time if hasattr(self.monitoring_group, 'end_time') else 'N/A'
            is_done = self.monitoring_group.is_done

            return (f"Data from {self.user.username} at {self.timestamp} "
                    f"for {self.food_type if self.food_type else 'N/A'} | "
                    f"Spoilage Status: {self.get_spoilage_status_display()} | "
                    f"Monitoring Group ID: {group_id}, "
                    f"Start Time: {start_time}, "
                    f"End Time: {end_time}, "
                    f"Is Done: {is_done}")
        else:
            return f"Data from at {self.timestamp} for {self.food_type if self.food_type else 'N/A'}"



class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    monitoring_group = models.ForeignKey(MonitoringGroup, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Track if the notification has been read

    def __str__(self):
        return f"Notification for {self.user.username} | {self.timestamp}"