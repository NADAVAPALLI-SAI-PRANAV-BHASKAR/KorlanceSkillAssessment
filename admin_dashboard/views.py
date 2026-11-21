import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.urls import reverse

from examinations.models import Student, ExamInvitation, ExamAttempt
from domains.models import Domain
from questions.models import Question
from proctoring.models import ProctoringIncident
from email_service.models import EmailLog, SMTPSettings
from email_service.services import send_invitation_email, send_admin_report_email, get_active_smtp_config
from .services import generate_consolidated_excel_report, parse_student_excel_roster

@staff_member_required(login_url='admin_login')
def dashboard_view(request):
    """
    Enterprise Executive Assessment Analytics Dashboard.
    """
    total_students = Student.objects.count()
    invitations_sent = ExamInvitation.objects.filter(email_sent=True).count()
    total_attempts = ExamAttempt.objects.count()
    completed_exams = ExamAttempt.objects.filter(is_submitted=True).count()
    pending_exams = max(0, total_students - completed_exams)

    cat_1_count = ExamAttempt.objects.filter(is_submitted=True, performance_category='CATEGORY_1').count()
    cat_2_count = ExamAttempt.objects.filter(is_submitted=True, performance_category='CATEGORY_2').count()
    cat_3_count = ExamAttempt.objects.filter(is_submitted=True, performance_category='CATEGORY_3').count()

    avg_score = ExamAttempt.objects.filter(is_submitted=True).aggregate(Avg('total_score'))['total_score__avg'] or 0.0
    total_incidents = ProctoringIncident.objects.count()
    flagged_attempts_count = ExamAttempt.objects.filter(proctoring_incidents__isnull=False).distinct().count()

    # Domain breakdown
    domain_stats = Domain.objects.annotate(
        student_count=Count('students', distinct=True),
        completed_count=Count('exam_attempts', filter=Q(exam_attempts__is_submitted=True), distinct=True)
    ).order_by('-student_count')[:10]

    domain_labels = [d.name[:22] for d in domain_stats]
    domain_counts = [d.completed_count for d in domain_stats]

    recent_attempts = ExamAttempt.objects.select_related('student', 'domain').order_by('-started_at')[:8]

    context = {
        'total_students': total_students,
        'invitations_sent': invitations_sent,
        'total_attempts': total_attempts,
        'completed_exams': completed_exams,
        'pending_exams': pending_exams,
        'cat_1_count': cat_1_count,
        'cat_2_count': cat_2_count,
        'cat_3_count': cat_3_count,
        'avg_score': round(avg_score, 1),
        'total_incidents': total_incidents,
        'flagged_attempts_count': flagged_attempts_count,
        'domain_labels_json': json.dumps(domain_labels),
        'domain_counts_json': json.dumps(domain_counts),
        'cat_data_json': json.dumps([cat_1_count, cat_2_count, cat_3_count]),
        'recent_attempts': recent_attempts,
        'page_title': 'Executive Assessment Intelligence Dashboard — KORLANCE'
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@staff_member_required(login_url='admin_login')
def students_view(request):
    """
    Searchable candidate roster with filtering and attempt details.
    """
    query = request.GET.get('q', '').strip()
    domain_id = request.GET.get('domain', '')
    status_filter = request.GET.get('status', '')

    students = Student.objects.select_related('target_domain').prefetch_related('attempts').order_by('-created_at')

    if query:
        students = students.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile_number__icontains=query)
        )

    if domain_id:
        students = students.filter(target_domain_id=domain_id)

    if status_filter == 'COMPLETED':
        students = students.filter(attempts__is_submitted=True).distinct()
    elif status_filter == 'PENDING':
        students = students.exclude(attempts__is_submitted=True).distinct()

    domains = Domain.objects.filter(is_active=True).order_by('name')

    context = {
        'students': students[:100],  # Display top 100
        'total_count': students.count(),
        'domains': domains,
        'selected_domain': domain_id,
        'selected_status': status_filter,
        'search_query': query,
        'page_title': 'Candidate Management Roster — KORLANCE'
    }
    return render(request, 'admin_dashboard/students_list.html', context)


@staff_member_required(login_url='admin_login')
def excel_upload_view(request):
    """
    Upload and parse .xlsx / .xls student candidate rosters.
    Displays a validation preview and imports candidates on confirmation.
    """
    preview_data = None

    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            file_obj = request.FILES['excel_file']
            preview_data = parse_student_excel_roster(file_obj)
            request.session['excel_import_records'] = preview_data['records'] if preview_data['success'] else []
        elif 'confirm_import' in request.POST:
            records = request.session.get('excel_import_records', [])
            imported_count = 0
            for r in records:
                if r['is_valid']:
                    domain = Domain.objects.filter(id=r['domain_id']).first()
                    if domain:
                        student, created = Student.objects.update_or_create(
                            email=r['email'],
                            defaults={
                                'full_name': r['name'],
                                'mobile_number': r['mobile'],
                                'target_domain': domain,
                                'source': 'EXCEL_IMPORT'
                            }
                        )
                        # Generate unique invitation token
                        ExamInvitation.objects.get_or_create(
                            student=student,
                            domain=domain,
                            defaults={'is_used': False}
                        )
                        imported_count += 1
            request.session.pop('excel_import_records', None)
            messages.success(request, f"Successfully imported and generated invitations for {imported_count} candidates.")
            return redirect('invitations_list')

    context = {
        'preview_data': preview_data,
        'page_title': 'Excel Candidate Roster Ingestion — KORLANCE'
    }
    return render(request, 'admin_dashboard/excel_upload.html', context)


@staff_member_required(login_url='admin_login')
def invitations_view(request):
    """
    Manage candidate invitations and trigger bulk/single email dispatches.
    """
    if request.method == 'POST' and 'send_batch_invitations' in request.POST:
        pending_invitations = ExamInvitation.objects.filter(email_sent=False, is_used=False).select_related('student', 'domain')
        sent_count = 0
        failed_count = 0
        
        for inv in pending_invitations:
            inv_link = request.build_absolute_uri(reverse('register')) + f"?invite={inv.token}"
            success, msg = send_invitation_email(inv.student, inv_link)
            if success:
                inv.email_sent = True
                inv.email_sent_at = timezone.now()
                inv.save(update_fields=['email_sent', 'email_sent_at'])
                sent_count += 1
            else:
                failed_count += 1

        messages.info(request, f"Batch Invitation Results: {sent_count} delivered successfully, {failed_count} delivery failures.")
        return redirect('invitations_list')

    invitations = ExamInvitation.objects.select_related('student', 'domain').order_by('-created_at')[:100]
    context = {
        'invitations': invitations,
        'pending_count': ExamInvitation.objects.filter(email_sent=False, is_used=False).count(),
        'sent_count': ExamInvitation.objects.filter(email_sent=True).count(),
        'page_title': 'Assessment Invitation Management — KORLANCE'
    }
    return render(request, 'admin_dashboard/invitations_list.html', context)


@staff_member_required(login_url='admin_login')
def email_logs_view(request):
    """
    Email Dispatch and Delivery Audit Logs.
    """
    logs = EmailLog.objects.order_by('-sent_at')[:100]
    context = {
        'logs': logs,
        'page_title': 'Enterprise Email Delivery Logs — KORLANCE'
    }
    return render(request, 'admin_dashboard/email_logs.html', context)


@staff_member_required(login_url='admin_login')
def proctoring_view(request):
    """
    Proctoring Incident Monitoring & Incident Audit Review.
    """
    incidents = ProctoringIncident.objects.select_related('attempt__student', 'attempt__domain').order_by('-timestamp')[:100]
    
    # Flagged attempts summary
    flagged_attempts = ExamAttempt.objects.filter(proctoring_incidents__isnull=False).distinct().annotate(
        incident_count=Count('proctoring_incidents')
    ).order_by('-incident_count')[:25]

    context = {
        'incidents': incidents,
        'flagged_attempts': flagged_attempts,
        'page_title': 'Online Proctoring Incident Review — KORLANCE'
    }
    return render(request, 'admin_dashboard/proctoring_list.html', context)


@staff_member_required(login_url='admin_login')
def export_report_view(request):
    """
    Generates and exports the consolidated Excel assessment report.
    Can be downloaded directly or emailed to the corporate administrator.
    """
    action = request.GET.get('action', 'download')
    domain_id = request.GET.get('domain', None)
    
    excel_buffer = generate_consolidated_excel_report(domain_filter=domain_id)

    if action == 'email':
        config = get_active_smtp_config()
        admin_email = config['admin_recipient']
        success, msg = send_admin_report_email(excel_buffer, recipient=admin_email)
        if success:
            messages.success(request, f"Consolidated assessment report emailed to {admin_email}.")
        else:
            messages.error(request, f"Failed to email report: {msg}")
        return redirect('admin_dashboard')
    else:
        timestamp_str = timezone.now().strftime('%Y%m%d_%H%M')
        filename = f"KORLANCE_Assessment_Report_{timestamp_str}.xlsx"
        response = HttpResponse(excel_buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@staff_member_required(login_url='admin_login')
def question_bank_view(request):
    """
    Domain-Specific Question Bank Management.
    """
    domain_id = request.GET.get('domain', '')
    domains = Domain.objects.filter(is_active=True).order_by('name')
    
    selected_domain = domains.first()
    if domain_id:
        selected_domain = domains.filter(id=domain_id).first() or selected_domain

    questions = Question.objects.filter(domain=selected_domain).order_by('difficulty', 'id')

    # Handle question creation
    if request.method == 'POST' and 'create_question' in request.POST:
        q_text = request.POST.get('question_text')
        opt_a = request.POST.get('option_a')
        opt_b = request.POST.get('option_b')
        opt_c = request.POST.get('option_c')
        opt_d = request.POST.get('option_d')
        correct = request.POST.get('correct_option')
        difficulty = request.POST.get('difficulty', 'MEDIUM')
        explanation = request.POST.get('explanation', '')

        Question.objects.create(
            domain=selected_domain,
            question_text=q_text,
            option_a=opt_a,
            option_b=opt_b,
            option_c=opt_c,
            option_d=opt_d,
            correct_option=correct,
            difficulty=difficulty,
            explanation=explanation
        )
        messages.success(request, "New question successfully added to the domain question bank.")
        return redirect(f"{reverse('question_bank')}?domain={selected_domain.id}")

    context = {
        'domains': domains,
        'selected_domain': selected_domain,
        'questions': questions,
        'easy_count': questions.filter(difficulty='EASY').count(),
        'medium_count': questions.filter(difficulty='MEDIUM').count(),
        'hard_count': questions.filter(difficulty='HARD').count(),
        'page_title': 'Question Bank Management — KORLANCE'
    }
    return render(request, 'admin_dashboard/question_bank.html', context)


@staff_member_required(login_url='admin_login')
def smtp_settings_view(request):
    """
    SMTP & Notification Gateway Configuration.
    """
    config = SMTPSettings.objects.first()
    if not config:
        config = SMTPSettings.objects.create(
            host='smtp.gmail.com',
            port=587,
            use_tls=True,
            from_email='KORLANCE Assessments <assessments@korlance.com>',
            admin_recipient_email='Shaikbaji15102002@gmail.com'
        )

    if request.method == 'POST':
        config.host = request.POST.get('host', 'smtp.gmail.com').strip()
        config.port = int(request.POST.get('port', 587))
        config.use_tls = request.POST.get('use_tls') == 'on'
        config.username = request.POST.get('username', '').strip()
        new_pwd = request.POST.get('password', '').strip()
        if new_pwd:
            config.password = new_pwd
        config.from_email = request.POST.get('from_email', 'KORLANCE Assessments <assessments@korlance.com>').strip()
        config.admin_recipient_email = request.POST.get('admin_recipient_email', 'Shaikbaji15102002@gmail.com').strip()
        config.save()
        messages.success(request, "SMTP gateway and administrative notification settings updated successfully.")
        return redirect('smtp_settings')

    context = {
        'config': config,
        'page_title': 'SMTP Gateway & Email Settings — KORLANCE'
    }
    return render(request, 'admin_dashboard/smtp_settings.html', context)
