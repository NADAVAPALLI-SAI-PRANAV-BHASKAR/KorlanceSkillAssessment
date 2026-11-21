import random
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from .models import ExamAttempt, StudentAnswer
from questions.models import Question
from email_service.services import send_completion_email

def start_or_resume_exam_attempt(student, domain, invitation=None):
    """
    Retrieves an existing active attempt or generates a new randomized 50-question attempt.
    Enforces 15 Easy, 25 Medium, and 10 Hard questions distribution.
    Duration is strictly 40 minutes.
    """
    # 1. Check if student already has an active, unsubmitted attempt that hasn't expired
    active_attempt = ExamAttempt.objects.filter(
        student=student,
        domain=domain,
        is_submitted=False
    ).first()

    if active_attempt:
        # Check if expired
        if active_attempt.is_expired:
            evaluate_and_finalize_attempt(active_attempt, submission_type='AUTO_TIMEOUT')
        else:
            return active_attempt, False

    # 2. Check if already submitted (prevent re-attempts unless authorized)
    completed_attempt = ExamAttempt.objects.filter(
        student=student,
        domain=domain,
        is_submitted=True
    ).first()
    if completed_attempt:
        return completed_attempt, False

    # 3. Create fresh attempt
    with transaction.atomic():
        now = timezone.now()
        expires_at = now + timedelta(minutes=40)
        
        attempt = ExamAttempt.objects.create(
            student=student,
            domain=domain,
            invitation=invitation,
            duration_minutes=40,
            expires_at=expires_at,
            total_questions=50,
            max_score=100.0
        )

        # Retrieve questions by difficulty
        easy_qs = list(Question.objects.filter(domain=domain, difficulty='EASY', is_active=True))
        med_qs = list(Question.objects.filter(domain=domain, difficulty='MEDIUM', is_active=True))
        hard_qs = list(Question.objects.filter(domain=domain, difficulty='HARD', is_active=True))

        selected = []
        # Sample or take available
        selected += random.sample(easy_qs, min(15, len(easy_qs)))
        selected += random.sample(med_qs, min(25, len(med_qs)))
        selected += random.sample(hard_qs, min(10, len(hard_qs)))

        # Fallback if any difficulty has fewer questions
        if len(selected) < 50:
            remaining_needed = 50 - len(selected)
            remaining_qs = list(Question.objects.filter(domain=domain, is_active=True).exclude(id__in=[q.id for q in selected]))
            selected += random.sample(remaining_qs, min(remaining_needed, len(remaining_qs)))

        # Shuffle selected questions to ensure a randomized sequence
        random.shuffle(selected)

        # Create answer records
        answers_to_create = []
        for idx, q in enumerate(selected, start=1):
            answers_to_create.append(StudentAnswer(
                attempt=attempt,
                question=q,
                order=idx,
                is_visited=(idx == 1) # First question is visited by default
            ))
        StudentAnswer.objects.bulk_create(answers_to_create)

        if invitation:
            invitation.is_used = True
            invitation.save(update_fields=['is_used'])

        return attempt, True


def record_student_response(attempt, question_id, selected_option=None, is_marked_for_review=False, is_visited=True):
    """
    Saves student answer selection and status continuously.
    Prevents modifications if attempt has expired or is submitted.
    """
    if attempt.is_submitted:
        return False, "Examination already finalized."
    
    if attempt.is_expired:
        evaluate_and_finalize_attempt(attempt, submission_type='AUTO_TIMEOUT')
        return False, "Examination time expired."

    try:
        answer = StudentAnswer.objects.get(attempt=attempt, question_id=question_id)
        if selected_option in ['A', 'B', 'C', 'D']:
            answer.selected_option = selected_option
            answer.answered_at = timezone.now()
        elif selected_option == 'CLEAR':
            answer.selected_option = None
            answer.answered_at = None

        answer.is_marked_for_review = is_marked_for_review
        answer.is_visited = is_visited
        answer.save()
        return True, "Response recorded."
    except StudentAnswer.DoesNotExist:
        return False, "Question not associated with this assessment."


def evaluate_and_finalize_attempt(attempt, submission_type='MANUAL'):
    """
    Evaluates examination responses on the server side securely.
    Assigns performance category and automatically triggers confirmation email.
    """
    if attempt.is_submitted:
        return attempt

    with transaction.atomic():
        answers = attempt.answers.select_related('question').all()
        
        correct_count = 0
        incorrect_count = 0
        unanswered_count = 0
        total_score = 0.0

        for ans in answers:
            q = ans.question
            if ans.selected_option:
                if ans.selected_option.upper() == q.correct_option.upper():
                    ans.is_correct = True
                    correct_count += 1
                    total_score += q.marks
                else:
                    ans.is_correct = False
                    incorrect_count += 1
            else:
                ans.is_correct = False
                unanswered_count += 1
            ans.save(update_fields=['is_correct'])

        percentage = round((total_score / attempt.max_score) * 100, 2)

        # Performance Categories:
        # 86-100: Category 1 – Excellent
        # 71-85:  Category 2 – Good
        # 0-70:   Category 3 – Needs Improvement
        if total_score >= 86:
            perf_cat = 'CATEGORY_1'
            cat_title = 'Category 1 – Excellent'
        elif total_score >= 71:
            perf_cat = 'CATEGORY_2'
            cat_title = 'Category 2 – Good'
        else:
            perf_cat = 'CATEGORY_3'
            cat_title = 'Category 3 – Needs Improvement'

        attempt.is_submitted = True
        attempt.submitted_at = timezone.now()
        attempt.submission_type = submission_type
        attempt.correct_answers = correct_count
        attempt.incorrect_answers = incorrect_count
        attempt.unanswered_questions = unanswered_count
        attempt.total_score = total_score
        attempt.percentage = percentage
        attempt.performance_category = perf_cat
        attempt.category_title = cat_title
        attempt.save()

    # Trigger automatic confirmation email
    try:
        send_completion_email(attempt)
    except Exception as e:
        # Do not block examination return if SMTP encounters network latency
        pass

    return attempt
