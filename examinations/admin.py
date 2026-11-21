from django.contrib import admin
from .models import Student, ExamInvitation, CandidateDeclaration, ExamAttempt, StudentAnswer

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'mobile_number', 'target_domain', 'source', 'is_invited', 'created_at')
    list_filter = ('target_domain', 'source', 'is_invited')
    search_fields = ('full_name', 'email', 'mobile_number')

@admin.register(ExamInvitation)
class ExamInvitationAdmin(admin.ModelAdmin):
    list_display = ('student', 'domain', 'token', 'is_used', 'email_sent', 'expires_at', 'created_at')
    list_filter = ('domain', 'is_used', 'email_sent')
    search_fields = ('student__full_name', 'student__email', 'token')

@admin.register(CandidateDeclaration)
class CandidateDeclarationAdmin(admin.ModelAdmin):
    list_display = ('student', 'ip_address', 'accepted_at')
    search_fields = ('student__full_name', 'student__email', 'ip_address')

class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    fields = ('order', 'question', 'selected_option', 'is_correct', 'is_marked_for_review')
    readonly_fields = ('order', 'question', 'selected_option', 'is_correct', 'is_marked_for_review')
    can_delete = False

@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'domain', 'started_at', 'is_submitted', 'submission_type', 'total_score', 'percentage', 'performance_category')
    list_filter = ('domain', 'is_submitted', 'performance_category', 'submission_type')
    search_fields = ('student__full_name', 'student__email', 'session_token')
    inlines = [StudentAnswerInline]
