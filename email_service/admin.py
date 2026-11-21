from django.contrib import admin
from .models import EmailLog, SMTPSettings

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_email', 'recipient_name', 'email_type', 'subject', 'status', 'sent_at')
    list_filter = ('email_type', 'status', 'sent_at')
    search_fields = ('recipient_email', 'recipient_name', 'subject', 'error_message')

@admin.register(SMTPSettings)
class SMTPSettingsAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'use_tls', 'from_email', 'admin_recipient_email', 'is_active', 'updated_at')
