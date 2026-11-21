from django.contrib import admin
from .models import ProctoringIncident

@admin.register(ProctoringIncident)
class ProctoringIncidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt_student', 'incident_type', 'timestamp', 'is_reviewed', 'reviewed_by')
    list_filter = ('incident_type', 'is_reviewed', 'timestamp')
    search_fields = ('attempt__student__full_name', 'attempt__student__email', 'details')

    def attempt_student(self, obj):
        return f"{obj.attempt.student.full_name} ({obj.attempt.domain.name})"
    attempt_student.short_description = "Candidate"
