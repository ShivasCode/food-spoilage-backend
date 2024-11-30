from rest_framework import generics
from sensor.models import MonitoringGroup, Notification, SensorData
from sensor.serializers import MonitoringGroupSerializer, MonitoringGroupDetailSerializer, SensorDataSerializer, SensorDataFormattedSerializer, NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


import pandas as pd
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MonitoringGroup
import os
from datetime import datetime
from django.template.loader import render_to_string
from rest_framework.pagination import PageNumberPagination

from django.utils import timezone

class SensorDataPagination(PageNumberPagination):
    page_size = 10  # Set page size to 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SensorDataCreateAPIView(generics.CreateAPIView):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer
    permission_classes = [IsAuthenticated]


class MonitoringGroupListView(generics.ListAPIView):
    serializer_class = MonitoringGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only the monitoring groups for the authenticated user, ordered by latest start_time
        return MonitoringGroup.objects.filter(user=self.request.user).order_by('-start_time')

class MonitoringGroupDetailView(generics.RetrieveAPIView):
    queryset = MonitoringGroup.objects.all()
    serializer_class = MonitoringGroupDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Fetch the monitoring group by ID
            monitoring_group = MonitoringGroup.objects.get(id=kwargs['pk'], user=request.user)

            # Get sensor data associated with the monitoring group, ordered from latest to oldest
            sensor_data = monitoring_group.sensor_data.order_by('-timestamp')  # Change to descending order

            # Serialize the monitoring group, including the sensor data
            serializer = self.get_serializer(monitoring_group)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except MonitoringGroup.DoesNotExist:
            return Response(
                {"error": "Monitoring group not found or not associated with the current user."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
class MonitoringGroupCSVExportView(generics.RetrieveAPIView):
    queryset = MonitoringGroup.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Fetch the monitoring group
            monitoring_group = self.get_object()
            sensor_data = monitoring_group.sensor_data.order_by('timestamp')

            # Prepare data for CSV
            data = [{
                'Timestamp': sd.timestamp.strftime("%B %d, %Y, %I:%M %p"),
                'Temperature': sd.temperature,
                'Humidity': sd.humidity,
                'Methane': sd.methane,
                'Threshold': sd.threshold,
                'Food Type': sd.food_type,
                'Spoilage Status': sd.spoilage_status
            } for sd in sensor_data]

            # Create a DataFrame
            df = pd.DataFrame(data)

            # Define CSV file name
            csv_file_name = f"{monitoring_group.id}_{monitoring_group.food_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_file_path = os.path.join(settings.MEDIA_ROOT, csv_file_name)

            # Save DataFrame to CSV
            df.to_csv(csv_file_path, index=False)

            # Prepare email
            subject = f"Sensor Data for {monitoring_group.food_type} Monitoring Group"
            context = {
                'username': request.user.username,
                'food_type': monitoring_group.food_type,
                'monitoring_group_id': monitoring_group.id,
            }
            body = render_to_string('csv_email.html', context)
            email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [request.user.email])
            email.attach_file(csv_file_path)
            email.content_subtype = "html"  
            email.send()

            return Response({"message": "CSV file generated and sent via email successfully."}, status=200)
        except MonitoringGroup.DoesNotExist:
            return Response({"error": "Monitoring group not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class NotificationUpdateView(generics.UpdateAPIView):
    model = Notification
    fields = ['read']  
    http_method_names = ['post'] 

    def post(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.read = True  
        notification.save()

        return Response({"status": "success", "message": "Notification marked as read."})

    def get_object(self):
        # Get the notification by ID
        notification_id = self.kwargs['notification_id']
        return Notification.objects.get(id=notification_id)
    

class LatestSensorDataView(generics.ListAPIView):
    serializer_class = SensorDataFormattedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all active monitoring groups
        active_monitoring_groups = MonitoringGroup.objects.filter(is_done=False, user=self.request.user)

        if not active_monitoring_groups.exists():
            return []

        # Get the latest sensor data for each active monitoring group
        latest_sensor_data = []
        for group in active_monitoring_groups:
            latest_data = SensorData.objects.filter(monitoring_group=group).order_by('-timestamp').first()
            if latest_data:
                latest_sensor_data.append(latest_data)

        return latest_sensor_data

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset:
            return Response({'message': 'No active monitoring.'}, status=200)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class EndMonitoringView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the user's active monitoring groups that are not done
        active_monitoring_groups = MonitoringGroup.objects.filter(is_done=False, user=request.user)

        if not active_monitoring_groups.exists():
            return Response({'message': 'No active monitoring groups to end.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update each active monitoring group to set is_done=True
        active_monitoring_groups.update(is_done=True, end_time=timezone.now())

        return Response({'message': 'Active monitoring groups marked as done.'}, status=status.HTTP_200_OK)
    
class UnreadNotificationsListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the current user and fetch unread notifications
        user = self.request.user
        
        # Fetch notifications where the message contains 'has spoiled' 
        # and the notification is unread (read=False)
        return self.get_unread_notifications_with_spoilage(user)

    def get_unread_notifications_with_spoilage(self, user):
        """
        Function to retrieve unread notifications for a specific user
        where the message contains 'has spoiled'.
        """
        # Filter notifications by user, read status, and whether the message contains 'has spoiled'
        return Notification.objects.filter(
            user=user,
            read=False,
            message__icontains="has spoiled"
        )

class UnreadWarningNotificationsListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the current user and fetch unread notifications
        user = self.request.user
        
        # Call the function to get unread notifications starting with 'Warning:'
        return self.get_unread_notifications_starting_with_warning(user)

    def get_unread_notifications_starting_with_warning(self, user):
        """
        Function to retrieve unread notifications for a specific user
        where the message starts with 'Warning:'.
        """
        # Filter notifications by user, read status, and whether the message starts with 'Warning:'
        return Notification.objects.filter(
            user=user,
            read=False,
            message__startswith="Warning:"
        )
    
class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter notifications for the logged-in user
        return Notification.objects.filter(user=self.request.user).order_by('-timestamp')

@api_view(['PATCH'])
def mark_notification_as_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.read = True
        notification.save()
        return Response({"message": "Notification marked as read"})
    except Notification.DoesNotExist:
        return Response({"message": "Notification not found"}, status=404)
    

@api_view(['DELETE'])
def delete_all_read_notifications(request):
    """
    Delete all read notifications for the authenticated user.
    """
    if not request.user.is_authenticated:
        return Response({"message": "Authentication required"}, status=401)

    # Filter and delete all notifications that are read for the current user
    notifications = Notification.objects.filter(user=request.user, read=True)

    # Get the count of deleted notifications
    deleted_count, _ = notifications.delete()

    # Return a response indicating how many notifications were deleted
    return Response({"message": f"{deleted_count} read notifications deleted."}, status=200)

from rest_framework.views import APIView


class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this API

    def get(self, request):
        # Check if the user has unread notifications
        unread_exists = Notification.objects.filter(user=request.user, read=False).exists()

        # Return a boolean indicating if there are unread notifications
        return Response({'unread_notifications': unread_exists})