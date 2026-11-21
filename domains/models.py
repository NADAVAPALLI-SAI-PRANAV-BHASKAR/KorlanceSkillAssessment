from django.db import models
from django.utils.text import slugify

class Domain(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text="Official Domain Name")
    code = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True)
    badge = models.CharField(max_length=50, default="Core Discipline")
    icon_name = models.CharField(max_length=50, default="layers")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Assessment Domain'
        verbose_name_plural = 'Assessment Domains'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def question_count(self):
        return self.questions.filter(is_active=True).count()
