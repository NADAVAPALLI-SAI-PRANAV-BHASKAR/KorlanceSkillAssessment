from django.conf import settings
from django.utils import timezone

def korlance_branding(request):
    return {
        'BRAND_NAME': 'KORLANCE PRIVATE LIMITED',
        'BRAND_SHORT': 'KORLANCE',
        'BRAND_TAGLINE': 'BUILD TODAY, LEAD TOMORROW.',
        'COLOR_PRIMARY': '#5213B3',
        'COLOR_DEEP': '#400C92',
        'COLOR_ACCENT': '#A855F7',
        'COLOR_LIGHT': '#F3EAFE',
        'COLOR_BG': '#F8F7FC',
        'COLOR_TEXT_MAIN': '#211A2E',
        'COLOR_TEXT_MUTED': '#777184',
        'EXAM_DURATION_MINUTES': getattr(settings, 'EXAM_DURATION_MINUTES', 40),
        'EXAM_TOTAL_QUESTIONS': getattr(settings, 'EXAM_TOTAL_QUESTIONS', 50),
        'EXAM_MAX_MARKS': getattr(settings, 'EXAM_MAX_MARKS', 100),
        'CURRENT_YEAR': timezone.now().year,
    }
