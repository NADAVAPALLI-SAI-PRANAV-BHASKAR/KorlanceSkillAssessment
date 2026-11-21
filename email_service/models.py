from django.db import models

class EmailLog(models.Model):
    TYPE_CHOICES = [
        ('INVITATION', 'Candidate Examination Invitation'),
        ('COMPLETION', 'Assessment Completion Confirmation'),
        ('ADMIN_REPORT', 'Admin Consolidated Excel Report'),
    ]

    STATUS_CHOICES = [
        ('SENT', 'Successfully Delivered'),
        ('FAILED', 'Delivery Failed'),
        ('PENDING', 'Queued / In Progress'),
    ]

    recipient_email = models.EmailField(db_index=True)
    recipient_name = models.CharField(max_length=200, blank=True)
    email_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Email Delivery Log'
        verbose_name_plural = 'Email Delivery Logs'

    def __str__(self):
        return f"[{self.status}] {self.email_type} -> {self.recipient_email}"


class SMTPSettings(models.Model):
    host = models.CharField(max_length=200, default='smtp.gmail.com')
    port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    username = models.CharField(max_length=200, blank=True)
    password = models.CharField(max_length=200, blank=True)
    from_email = models.CharField(max_length=200, default='KORLANCE Assessments <assessments@korlance.com>')
    admin_recipient_email = models.EmailField(default='Shaikbaji15102002@gmail.com', help_text="Consolidated exam report destination")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'SMTP & Delivery Configuration'
        verbose_name_plural = 'SMTP & Delivery Configuration'

    def __str__(self):
        return f"SMTP Config ({self.host}:{self.port}) - Admin: {self.admin_recipient_email}"
