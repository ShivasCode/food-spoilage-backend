from django.contrib import admin
from .models import SensorData, MonitoringGroup, Notification


class MonitoringGroupIDFilter(admin.SimpleListFilter):
    title = 'Monitoring Group ID'  # Display title for the filter in the admin panel
    parameter_name = 'monitoring_group_id'  # Query parameter name

    def lookups(self, request, model_admin):
        # Return a list of tuples (value, label) for the filter options
        monitoring_groups = model_admin.model.objects.values_list(
            'monitoring_group__id', flat=True
        ).distinct()
        return [(group_id, str(group_id)) for group_id in monitoring_groups if group_id]

    def queryset(self, request, queryset):
        # Filter the queryset based on the selected value
        if self.value():
            return queryset.filter(monitoring_group__id=self.value())
        return queryset


class SensorDataAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'get_monitoring_group_id', 'temperature', 'humidity',
        'methane', 'ammonia', 'threshold', 'timestamp', 'food_type', 'display_spoilage_status'
    )
    list_filter = (
        'user', 'food_type', 'monitoring_group__is_done', 'timestamp',
        MonitoringGroupIDFilter  # Add the custom filter here
    )
    search_fields = ('user__username', 'food_type', 'monitoring_group__id')
    date_hierarchy = 'timestamp'  # Allows for filtering by date
    ordering = ('-timestamp',)  # Order by timestamp descending

    fieldsets = (
        (None, {
            'fields': ('user', 'monitoring_group')
        }),
        ('Sensor Readings', {
            'fields': ('temperature', 'humidity', 'methane', 'threshold', 'ammonia', 'food_type', 'spoilage_status', 'timestamp')
        }),
    )

    def get_monitoring_group_id(self, obj):
        return obj.monitoring_group.id if obj.monitoring_group else 'N/A'

    get_monitoring_group_id.short_description = 'Monitoring Group ID'  # Label for the column in the admin

    def display_spoilage_status(self, obj):
        return obj.spoilage_status  # Explicitly returning spoilage_status value

    display_spoilage_status.short_description = 'Spoilage Status'

class MonitoringGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'food_type', 'start_time', 'end_time', 'is_done')
    list_filter = ('user', 'food_type', 'is_done')
    search_fields = ('user__username', 'food_type')
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)

    fieldsets = (
        (None, {
            'fields': ('user', 'food_type', 'start_time', 'end_time', 'is_done','email_notification_sent', 'phone_notification_sent')
        }),
    )

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'monitoring_group', 'message', 'timestamp', 'read')
    list_filter = ('user', 'read', 'monitoring_group')
    search_fields = ('user__username', 'message')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

    fieldsets = (
        (None, {
            'fields': ('user', 'monitoring_group')
        }),
        ('Notification Details', {
            'fields': ('message', 'read')
        }),
    )

    # Optionally, you can add bulk actions for notifications
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
        self.message_user(request, "Selected notifications marked as read.")

    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
        self.message_user(request, "Selected notifications marked as unread.")

    mark_as_unread.short_description = "Mark selected notifications as unread"

# Registering the models with their respective admin classes
admin.site.register(SensorData, SensorDataAdmin)
admin.site.register(MonitoringGroup, MonitoringGroupAdmin)
admin.site.register(Notification, NotificationAdmin)