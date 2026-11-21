from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from examinations.models import ExamAttempt
from .services import generate_result_pdf

def results_view(request, session_token):
    """
    Renders official post-examination performance results page.
    """
    attempt = get_object_or_404(ExamAttempt, session_token=session_token)

    # Category messages
    category_messages = {
        'CATEGORY_1': {
            'title': 'Category 1 – Excellent',
            'desc': 'Congratulations! You have demonstrated excellent knowledge and understanding of your selected domain.',
            'badge_color': 'bg-emerald-50 text-emerald-700 border-emerald-200',
            'pill_color': 'bg-emerald-600',
        },
        'CATEGORY_2': {
            'title': 'Category 2 – Good',
            'desc': 'Great work! You have a good understanding of your domain. Keep improving your skills.',
            'badge_color': 'bg-amber-50 text-amber-700 border-amber-200',
            'pill_color': 'bg-amber-500',
        },
        'CATEGORY_3': {
            'title': 'Category 3 – Needs Improvement',
            'desc': 'Keep learning and practising. Strengthen your fundamentals and continue improving your domain knowledge.',
            'badge_color': 'bg-rose-50 text-rose-700 border-rose-200',
            'pill_color': 'bg-rose-600',
        }
    }

    current_cat_info = category_messages.get(attempt.performance_category, category_messages['CATEGORY_3'])

    context = {
        'attempt': attempt,
        'student': attempt.student,
        'domain': attempt.domain,
        'cat_info': current_cat_info,
        'page_title': f"Assessment Results — {attempt.student.full_name} | KORLANCE"
    }
    return render(request, 'results/results_view.html', context)


def download_pdf_view(request, session_token):
    """
    Exports official signed PDF assessment certificate.
    """
    attempt = get_object_or_404(ExamAttempt, session_token=session_token)
    pdf_buffer = generate_result_pdf(attempt)
    
    filename = f"KORLANCE_Assessment_Result_KOR{attempt.id:06d}.pdf"
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
