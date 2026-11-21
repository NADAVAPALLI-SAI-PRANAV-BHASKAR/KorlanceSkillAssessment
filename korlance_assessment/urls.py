from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.views import home_view
from examinations.views import (
    register_view,
    instructions_view,
    exam_room_view,
    save_answer_api,
    submit_exam_view
)
from results.views import results_view, download_pdf_view
from proctoring.views import log_incident_api
from accounts.views import admin_login_view, admin_logout_view
from admin_dashboard.views import (
    dashboard_view,
    students_view,
    excel_upload_view,
    invitations_view,
    email_logs_view,
    proctoring_view,
    export_report_view,
    question_bank_view,
    smtp_settings_view
)

urlpatterns = [
    # Candidate Examination Lifecycle
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('instructions/', instructions_view, name='instructions'),
    path('exam/<str:session_token>/', exam_room_view, name='exam_room'),
    path('exam/save-answer/', save_answer_api, name='save_answer'),
    path('exam/submit/', submit_exam_view, name='submit_exam'),
    path('results/<str:session_token>/', results_view, name='results'),
    path('results/<str:session_token>/download-pdf/', download_pdf_view, name='download_pdf'),

    # Proctoring Real-Time Telemetry
    path('proctoring/log-incident/', log_incident_api, name='log_incident'),

    # Corporate Administrator Authentication
    path('admin-portal/login/', admin_login_view, name='admin_login'),
    path('admin-portal/logout/', admin_logout_view, name='admin_logout'),

    # Enterprise Executive Administration Portal
    path('admin-portal/', dashboard_view, name='admin_dashboard'),
    path('admin-portal/students/', students_view, name='students_list'),
    path('admin-portal/excel-upload/', excel_upload_view, name='excel_upload'),
    path('admin-portal/invitations/', invitations_view, name='invitations_list'),
    path('admin-portal/email-logs/', email_logs_view, name='email_logs'),
    path('admin-portal/proctoring/', proctoring_view, name='proctoring_list'),
    path('admin-portal/reports/export/', export_report_view, name='export_report'),
    path('admin-portal/question-bank/', question_bank_view, name='question_bank'),
    path('admin-portal/smtp/', smtp_settings_view, name='smtp_settings'),

    # Standard Django Superuser Admin
    path('django-admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
