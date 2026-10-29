from django.contrib import admin
from .models import FollowUpReminder


@admin.register(FollowUpReminder)
class FollowUpReminderAdmin(admin.ModelAdmin):
    list_display = ("id", "medical_record", "scheduled_for", "status", "sent_at")
    list_filter = ("status", "scheduled_for")
    readonly_fields = (
        "medical_record",
        "scheduled_for",
        "status",
        "provider_reference",
        "error_message",
        "created_at",
        "updated_at",
        "sent_at",
    )

    def has_add_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return False
