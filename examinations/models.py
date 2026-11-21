import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from domains.models import Domain
from questions.models import Question

class Student(models.Model):
    SOURCE_CHOICES = [
        ('SELF_REGISTERED', 'Self Registered'),
        ('EXCEL_IMPORT', 'Excel Roster Import'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField(db_index=True)
    mobile_number = models.CharField(max_length=20, db_index=True)
    target_domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='students')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='SELF_REGISTERED')
    is_invited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Candidate / Student'
        verbose_name_plural = 'Candidates & Students'

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def latest_attempt(self):
        return self.attempts.order_by('-started_at').first()

    @property
    def has_completed_exam(self):
        return self.attempts.filter(is_submitted=True).exists()


class ExamInvitation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invitations')
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    is_used = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Examination Invitation'
        verbose_name_plural = 'Examination Invitations'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired


class CandidateDeclaration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='declarations')
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    declaration_text = models.TextField()

    def __str__(self):
        return f"Declaration: {self.student.full_name} at {self.accepted_at}"


class ExamAttempt(models.Model):
    SUBMISSION_CHOICES = [
        ('MANUAL', 'Manual Candidate Submission'),
        ('AUTO_TIMEOUT', 'Automatic Timer Expiration'),
        ('DISQUALIFIED', 'Proctoring Disqualification'),
    ]

    CATEGORY_CHOICES = [
        ('CATEGORY_1', 'Category 1 – Excellent'),
        ('CATEGORY_2', 'Category 2 – Good'),
        ('CATEGORY_3', 'Category 3 – Needs Improvement'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attempts')
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='exam_attempts')
    invitation = models.ForeignKey(ExamInvitation, on_delete=models.SET_NULL, null=True, blank=True)
    session_token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    
    started_at = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField(default=40)
    expires_at = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_CHOICES, default='MANUAL')
    
    # Evaluation Metrics
    total_questions = models.PositiveSmallIntegerField(default=50)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    incorrect_answers = models.PositiveSmallIntegerField(default=0)
    unanswered_questions = models.PositiveSmallIntegerField(default=50)
    total_score = models.FloatField(default=0.0)
    max_score = models.FloatField(default=100.0)
    percentage = models.FloatField(default=0.0)
    performance_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True)
    category_title = models.CharField(max_length=100, blank=True)
    
    # Completion email status
    completion_email_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Examination Attempt'
        verbose_name_plural = 'Examination Attempts'

    def save(self, *args, **kwargs):
        if self.session_token:
            self.session_token = str(self.session_token)
        if not self.expires_at and self.started_at:
            self.expires_at = self.started_at + timedelta(minutes=self.duration_minutes)
        elif not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=self.duration_minutes)
        super().save(*args, **kwargs)

    @property
    def remaining_seconds(self):
        if self.is_submitted:
            return 0
        diff = (self.expires_at - timezone.now()).total_seconds()
        return max(0, int(diff))

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)
    selected_option = models.CharField(max_length=1, blank=True, null=True)
    is_marked_for_review = models.BooleanField(default=False)
    is_visited = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"Attempt {self.attempt_id} - Q#{self.order} ({self.selected_option or 'None'})"
