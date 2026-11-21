from django.contrib import admin
from .models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain', 'difficulty', 'question_preview', 'correct_option', 'marks', 'is_active')
    list_filter = ('domain', 'difficulty', 'correct_option', 'is_active')
    search_fields = ('question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'explanation')
    list_per_page = 50

    def question_preview(self, obj):
        return obj.question_text[:75] + ("..." if len(obj.question_text) > 75 else "")
    question_preview.short_description = "Question Stem"
