import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from examinations.models import ExamAttempt
from .models import ProctoringIncident

@require_POST
def log_incident_api(request):
    """
    Receives proctoring telemetry from examination browser client.
    Logs tab switches, window blur events, webcam status alerts, and fullscreen exits.
    """
    try:
        data = json.loads(request.body)
        session_token = data.get('session_token')
        incident_type = data.get('incident_type')
        details = data.get('details', '')

        attempt = ExamAttempt.objects.filter(session_token=session_token, is_submitted=False).first()
        if not attempt:
            return JsonResponse({'success': False, 'error': 'Invalid session or examination already completed'}, status=400)

        incident = ProctoringIncident.objects.create(
            attempt=attempt,
            incident_type=incident_type,
            details=details
        )

        return JsonResponse({
            'success': True,
            'incident_id': incident.id,
            'total_incidents': attempt.proctoring_incidents.count()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
