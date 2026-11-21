import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import EmailLog, SMTPSettings

logger = logging.getLogger(__name__)

def get_active_smtp_config():
    """
    Returns the active database SMTP config or fallback to settings.py.
    """
    config = SMTPSettings.objects.filter(is_active=True).first()
    if config:
        return {
            'host': config.host,
            'port': config.port,
            'use_tls': config.use_tls,
            'username': config.username,
            'password': config.password,
            'from_email': config.from_email,
            'admin_recipient': config.admin_recipient_email
        }
    return {
        'host': getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
        'port': getattr(settings, 'EMAIL_PORT', 587),
        'use_tls': getattr(settings, 'EMAIL_USE_TLS', True),
        'username': getattr(settings, 'EMAIL_HOST_USER', ''),
        'password': getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'KORLANCE Assessments <assessments@korlance.com>'),
        'admin_recipient': getattr(settings, 'ADMIN_REPORT_EMAIL', 'Shaikbaji15102002@gmail.com')
    }

def send_invitation_email(student, invitation_link):
    """
    Sends official branded MNC examination invitation email.
    """
    subject = f"Official Assessment Invitation – {student.target_domain.name} | KORLANCE"
    context = {
        'student': student,
        'domain': student.target_domain,
        'invitation_link': invitation_link,
        'duration_minutes': 40,
        'total_questions': 50,
        'max_marks': 100,
        'brand_name': 'KORLANCE PRIVATE LIMITED',
        'tagline': 'BUILD TODAY, LEAD TOMORROW.',
    }
    
    html_content = render_to_string('email_service/invitation_email.html', context)
    text_content = strip_tags(html_content)
    
    log = EmailLog.objects.create(
        recipient_email=student.email,
        recipient_name=student.full_name,
        email_type='INVITATION',
        subject=subject,
        status='PENDING'
    )

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
        log.status = 'SENT'
        log.save()
        return True, "Email dispatched successfully."
    except Exception as e:
        logger.error(f"Failed to send invitation email to {student.email}: {str(e)}")
        log.status = 'FAILED'
        log.error_message = str(e)
        log.save()
        return False, str(e)


def send_completion_email(exam_attempt):
    """
    Sends automated assessment completion confirmation email upon exam submission.
    """
    student = exam_attempt.student
    subject = "Examination Successfully Completed – KORLANCE"
    
    context = {
        'student': student,
        'domain': exam_attempt.domain,
        'submitted_at': exam_attempt.submitted_at,
        'brand_name': 'KORLANCE PRIVATE LIMITED',
        'tagline': 'BUILD TODAY, LEAD TOMORROW.',
    }
    
    html_content = render_to_string('email_service/completion_email.html', context)
    text_content = strip_tags(html_content)

    log = EmailLog.objects.create(
        recipient_email=student.email,
        recipient_name=student.full_name,
        email_type='COMPLETION',
        subject=subject,
        status='PENDING'
    )

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
        log.status = 'SENT'
        log.save()
        exam_attempt.completion_email_sent = True
        exam_attempt.save(update_fields=['completion_email_sent'])
        return True, "Completion confirmation sent."
    except Exception as e:
        logger.error(f"Failed to send completion email to {student.email}: {str(e)}")
        log.status = 'FAILED'
        log.error_message = str(e)
        log.save()
        return False, str(e)


def send_admin_report_email(excel_buffer, filename="KORLANCE_Consolidated_Assessment_Results.xlsx", recipient=None):
    """
    Dispatches consolidated Excel report to the corporate administrator.
    Default recipient: Shaikbaji15102002@gmail.com
    """
    if not recipient:
        config = get_active_smtp_config()
        recipient = config['admin_recipient']

    subject = "KORLANCE – Consolidated Online Examination Results Report"
    
    context = {
        'recipient_email': recipient,
        'brand_name': 'KORLANCE PRIVATE LIMITED',
        'tagline': 'BUILD TODAY, LEAD TOMORROW.',
    }
    
    html_content = render_to_string('email_service/admin_report_email.html', context)
    text_content = strip_tags(html_content)

    log = EmailLog.objects.create(
        recipient_email=recipient,
        recipient_name="Assessment Administrator",
        email_type='ADMIN_REPORT',
        subject=subject,
        status='PENDING'
    )

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient]
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Attach the Excel workbook
        excel_buffer.seek(0)
        msg.attach(filename, excel_buffer.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        msg.send(fail_silently=False)
        
        log.status = 'SENT'
        log.save()
        return True, f"Consolidated report successfully emailed to {recipient}."
    except Exception as e:
        logger.error(f"Failed to send admin report email to {recipient}: {str(e)}")
        log.status = 'FAILED'
        log.error_message = str(e)
        log.save()
        return False, str(e)
