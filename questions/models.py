from django.db import models
from domains.models import Domain

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    ]

    OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(help_text="Detailed multiple-choice question stem")
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES, help_text="A, B, C, or D")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MEDIUM')
    marks = models.PositiveSmallIntegerField(default=2)
    explanation = models.TextField(blank=True, help_text="Technical explanation or rationale")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['domain', 'difficulty', 'id']
        verbose_name = 'Domain Question'
        verbose_name_plural = 'Domain Question Bank'

    def __str__(self):
        return f"[{self.domain.name}] [{self.difficulty}] {self.question_text[:60]}..."

    @property
    def correct_answer_text(self):
        lookup = {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }
        return lookup.get(self.correct_option, "")
