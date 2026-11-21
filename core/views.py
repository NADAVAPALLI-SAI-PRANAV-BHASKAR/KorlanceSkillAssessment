from django.shortcuts import render
from domains.models import Domain

def home_view(request):
    """
    KORLANCE Enterprise Assessment Portal - Landing Page.
    """
    domains = Domain.objects.filter(is_active=True).order_by('name')
    context = {
        'domains': domains,
        'page_title': 'Enterprise Assessment & Certification Portal'
    }
    return render(request, 'core/landing.html', context)
