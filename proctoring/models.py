from django.db import models
from django.contrib.auth.models import User
from examinations.models import ExamAttempt

class ProctoringIncident(models.Model):
    INCIDENT_TYPES = [
        ('TAB_SWITCH', 'Browser Tab Switched'),
        ('WINDOW_BLUR', 'Examination Window Lost Focus'),
        ('NO_FACE_DETECTED', 'No Candidate Face Detected'),
        ('MULTIPLE_FACES', 'Multiple Faces Detected in Camera'),
        ('FULLSCREEN_EXIT', 'Exited Mandatory Fullscreen Mode'),
        ('SUSPICIOUS_KEY', 'Restricted Key Combination Detected'),
    ]

    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='proctoring_incidents')
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPES)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Proctoring Incident'
        verbose_name_plural = 'Proctoring Incidents'

    def __str__(self):
        return f"[{self.get_incident_type_display()}] Attempt {self.attempt_id} at {self.timestamp}"
