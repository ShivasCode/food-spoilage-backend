from django.urls import path
from sensor.views import (MonitoringGroupListView, MonitoringGroupDetailView, 
                          MonitoringGroupCSVExportView, NotificationUpdateView, LatestSensorDataView, 
                          EndMonitoringView,SensorDataCreateAPIView, UnreadNotificationsListView, 
                          UnreadWarningNotificationsListView, NotificationListAPIView, mark_notification_as_read, delete_all_read_notifications,
                          UnreadNotificationCountView)

urlpatterns = [

    path('sensor-data/', SensorDataCreateAPIView.as_view(), name='sensor-data-create'),

    # List all monitoring groups
    path('monitoring-groups/', MonitoringGroupListView.as_view(), name='monitoring-group-list'),
    
    # Retrieve specific monitoring group by ID, with associated sensor data
    path('monitoring-groups/<int:pk>/', MonitoringGroupDetailView.as_view(), name='monitoring-group-detail'),
    path('monitoring-groups/<int:pk>/export-csv/', MonitoringGroupCSVExportView.as_view(), name='export-monitoring-group-csv'),
    path('notifications/acknowledge/<int:notification_id>/', NotificationUpdateView.as_view(), name='notification-acknowledge'),
    path('latest-sensor-data/', LatestSensorDataView.as_view(), name='latest-sensor-data'),
    path('end-monitoring/', EndMonitoringView.as_view(), name='end_monitoring'),

    path('notifications/unread/', UnreadNotificationsListView.as_view(), name='unread-notifications'),
    path('notifications/warnings/unread/', UnreadWarningNotificationsListView.as_view(), name='unread-notifications'),
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', mark_notification_as_read, name='mark-notification-read'),
        path('notifications/read/', delete_all_read_notifications, name='delete-all-read'),
        path('notifications/unread/count/', UnreadNotificationCountView.as_view(), name='unread-count'),

]
