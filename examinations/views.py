import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages

from .models import Student, ExamInvitation, CandidateDeclaration, ExamAttempt, StudentAnswer
from domains.models import Domain
from .services import start_or_resume_exam_attempt, record_student_response, evaluate_and_finalize_attempt

def register_view(request):
    """
    Student Registration View.
    Supports preselecting & locking domain when invited via secure token (?invite=TOKEN).
    """
    invite_token = request.GET.get('invite', '').strip()
    invitation = None
    locked_domain = None

    if invite_token:
        invitation = ExamInvitation.objects.filter(token=invite_token, is_used=False).first()
        if invitation:
            if invitation.is_expired:
                messages.error(request, "This examination invitation link has expired. Please contact support.")
            else:
                locked_domain = invitation.domain

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        mobile_number = request.POST.get('mobile_number', '').strip()
        domain_id = request.POST.get('domain_id', '')

        # Basic validation
        if not full_name or not email or not mobile_number:
            messages.error(request, "All fields are mandatory. Please fill in your name, email, and mobile number.")
            return redirect(request.get_full_path())

        if locked_domain:
            target_domain = locked_domain
        else:
            target_domain = get_object_or_404(Domain, id=domain_id, is_active=True)

        # Create or update student record
        student, _ = Student.objects.update_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'mobile_number': mobile_number,
                'target_domain': target_domain,
            }
        )

        # Store session identity
        request.session['assessment_student_id'] = student.id
        request.session['assessment_domain_id'] = target_domain.id
        if invitation:
            request.session['assessment_invite_id'] = invitation.id

        return redirect('instructions')

    domains = Domain.objects.filter(is_active=True).order_by('name')
    context = {
        'domains': domains,
        'invitation': invitation,
        'locked_domain': locked_domain,
        'page_title': 'Candidate Registration — KORLANCE Online Assessment'
    }
    return render(request, 'examinations/register.html', context)


def instructions_view(request):
    """
    Official Examination Instructions & Mandatory Candidate Declaration.
    """
    student_id = request.session.get('assessment_student_id')
    if not student_id:
        return redirect('register')

    student = get_object_or_404(Student, id=student_id)
    domain_id = request.session.get('assessment_domain_id', student.target_domain_id)
    domain = get_object_or_404(Domain, id=domain_id)

    # Check if candidate has already completed an exam in this domain
    completed_attempt = ExamAttempt.objects.filter(student=student, domain=domain, is_submitted=True).first()
    if completed_attempt:
        return redirect('results', session_token=completed_attempt.session_token)

    if request.method == 'POST':
        declaration_accepted = request.POST.get('declaration_accepted') == 'on'
        if not declaration_accepted:
            messages.error(request, "You must accept the candidate declaration to start the assessment.")
            return redirect('instructions')

        # Record candidate declaration audit
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        declaration_text = (
            "I hereby confirm that I have read and understood all the examination instructions and agree to follow the rules and regulations. "
            "I declare that I will complete the examination independently without using unauthorized resources or assistance. "
            "I understand that my examination activity may be monitored through the enabled proctoring features and that violations may result in review "
            "or disqualification according to the examination policy. By clicking 'I Agree & Start Examination,' I accept all the above conditions."
        )

        CandidateDeclaration.objects.create(
            student=student,
            ip_address=client_ip,
            user_agent=user_agent,
            declaration_text=declaration_text
        )

        # Check for invitation token if any
        invitation = None
        invite_id = request.session.get('assessment_invite_id')
        if invite_id:
            invitation = ExamInvitation.objects.filter(id=invite_id, is_used=False).first()

        # Start or resume the 40-minute attempt
        attempt, is_new = start_or_resume_exam_attempt(student, domain, invitation)

        return redirect('exam_room', session_token=attempt.session_token)

    context = {
        'student': student,
        'domain': domain,
        'page_title': 'Examination Instructions & Candidate Declaration'
    }
    return render(request, 'examinations/instructions.html', context)


def exam_room_view(request, session_token):
    """
    Live Enterprise Proctored Examination Interface.
    Features: 40-minute timer, 50 questions, palette navigation, webcam proctoring preview.
    """
    attempt = get_object_or_404(ExamAttempt, session_token=session_token)
    
    if attempt.is_submitted:
        return redirect('results', session_token=attempt.session_token)

    # Check if timer has expired on server
    if attempt.is_expired:
        evaluate_and_finalize_attempt(attempt, submission_type='AUTO_TIMEOUT')
        return redirect('results', session_token=attempt.session_token)

    answers = attempt.answers.select_related('question').order_by('order')
    
    # Package question data for client-side JavaScript engine
    questions_list = []
    answered_count = 0
    marked_count = 0

    for ans in answers:
        q = ans.question
        if ans.selected_option:
            answered_count += 1
        if ans.is_marked_for_review:
            marked_count += 1

        questions_list.append({
            'order': ans.order,
            'id': q.id,
            'difficulty': q.difficulty,
            'text': q.question_text,
            'options': {
                'A': q.option_a,
                'B': q.option_b,
                'C': q.option_c,
                'D': q.option_d,
            },
            'selected': ans.selected_option or '',
            'marked_for_review': ans.is_marked_for_review,
            'visited': ans.is_visited,
            'marks': q.marks
        })

    remaining_seconds = attempt.remaining_seconds

    context = {
        'attempt': attempt,
        'student': attempt.student,
        'domain': attempt.domain,
        'questions_json': json.dumps(questions_list),
        'remaining_seconds': remaining_seconds,
        'answered_count': answered_count,
        'marked_count': marked_count,
        'total_questions': attempt.total_questions,
        'page_title': f"{attempt.domain.name} — Proctored Examination | KORLANCE"
    }
    return render(request, 'examinations/exam_room.html', context)


@require_POST
def save_answer_api(request):
    """
    AJAX endpoint for continuous response saving.
    """
    try:
        data = json.loads(request.body)
        session_token = data.get('session_token')
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')
        is_marked_for_review = bool(data.get('is_marked_for_review', False))
        is_visited = bool(data.get('is_visited', True))

        attempt = ExamAttempt.objects.filter(session_token=session_token, is_submitted=False).first()
        if not attempt:
            return JsonResponse({'success': False, 'error': 'Invalid or finalized attempt'}, status=400)

        success, msg = record_student_response(
            attempt=attempt,
            question_id=question_id,
            selected_option=selected_option,
            is_marked_for_review=is_marked_for_review,
            is_visited=is_visited
        )

        return JsonResponse({
            'success': success,
            'message': msg,
            'remaining_seconds': attempt.remaining_seconds
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def submit_exam_view(request):
    """
    Handles candidate or timer-driven final submission.
    """
    session_token = request.POST.get('session_token')
    submission_type = request.POST.get('submission_type', 'MANUAL')

    attempt = get_object_or_404(ExamAttempt, session_token=session_token)
    evaluate_and_finalize_attempt(attempt, submission_type=submission_type)

    return redirect('results', session_token=attempt.session_token)
