import io
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from openpyxl import Workbook, load_workbook

from domains.models import Domain
from questions.models import Question
from examinations.models import Student, ExamInvitation, ExamAttempt, StudentAnswer, CandidateDeclaration
from proctoring.models import ProctoringIncident
from examinations.services import start_or_resume_exam_attempt, record_student_response, evaluate_and_finalize_attempt
from admin_dashboard.services import generate_consolidated_excel_report, parse_student_excel_roster
from results.services import generate_result_pdf

class KorlancePlatformTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Setup sample domains
        self.domain1 = Domain.objects.create(
            name="Artificial Intelligence & Machine Learning (AI & ML)",
            code="ai-ml",
            badge="Cutting Edge"
        )
        self.domain2 = Domain.objects.create(
            name="Full Stack Web Development",
            code="full-stack-web-development",
            badge="Enterprise Core"
        )

        # 2. Setup 50 questions for domain 1 (15 Easy, 25 Med, 10 Hard)
        for i in range(15):
            Question.objects.create(
                domain=self.domain1,
                question_text=f"Sample AI/ML Easy Question {i+1}?",
                option_a="Alpha", option_b="Beta", option_c="Gamma", option_d="Delta",
                correct_option="A", difficulty="EASY", marks=2
            )
        for i in range(25):
            Question.objects.create(
                domain=self.domain1,
                question_text=f"Sample AI/ML Medium Question {i+1}?",
                option_a="Alpha", option_b="Beta", option_c="Gamma", option_d="Delta",
                correct_option="B", difficulty="MEDIUM", marks=2
            )
        for i in range(10):
            Question.objects.create(
                domain=self.domain1,
                question_text=f"Sample AI/ML Hard Question {i+1}?",
                option_a="Alpha", option_b="Beta", option_c="Gamma", option_d="Delta",
                correct_option="C", difficulty="HARD", marks=2
            )

        # 3. Setup test student
        self.student = Student.objects.create(
            full_name="Jane Doe",
            email="jane.doe@korlance.com",
            mobile_number="9876543210",
            target_domain=self.domain1
        )

        # 4. Setup staff user
        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='Shaikbaji15102002@gmail.com',
            password='TestPassword123!'
        )

    def test_domain_question_count(self):
        """Verifies that domain1 has exactly 50 questions with 15/25/10 distribution."""
        self.assertEqual(self.domain1.questions.count(), 50)
        self.assertEqual(self.domain1.questions.filter(difficulty='EASY').count(), 15)
        self.assertEqual(self.domain1.questions.filter(difficulty='MEDIUM').count(), 25)
        self.assertEqual(self.domain1.questions.filter(difficulty='HARD').count(), 10)

    def test_candidate_registration_view(self):
        """Tests registration workflow and session persistence."""
        response = self.client.post(reverse('register'), {
            'full_name': 'Candidate Mark',
            'email': 'mark@test.com',
            'mobile_number': '+91 9988776655',
            'domain_id': self.domain1.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('instructions'))
        
        # Verify student created
        mark = Student.objects.get(email='mark@test.com')
        self.assertEqual(mark.full_name, 'Candidate Mark')
        self.assertEqual(mark.target_domain, self.domain1)

    def test_secure_invitation_preselection(self):
        """Verifies that ?invite=TOKEN locks the preselected domain."""
        invitation = ExamInvitation.objects.create(
            student=self.student,
            domain=self.domain2
        )
        response = self.client.get(f"{reverse('register')}?invite={invitation.token}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.domain2.name)

    def test_exam_attempt_generation_and_timer(self):
        """Verifies exam attempt initialization with 40-minute duration and exactly 50 randomized questions."""
        attempt, is_new = start_or_resume_exam_attempt(self.student, self.domain1)
        self.assertTrue(is_new)
        self.assertEqual(attempt.duration_minutes, 40)
        self.assertEqual(attempt.answers.count(), 50)
        self.assertFalse(attempt.is_submitted)
        self.assertGreater(attempt.remaining_seconds, 2300)

    def test_continuous_answer_autosave(self):
        """Verifies candidate response recording."""
        attempt, _ = start_or_resume_exam_attempt(self.student, self.domain1)
        first_ans = attempt.answers.first()

        success, msg = record_student_response(
            attempt=attempt,
            question_id=first_ans.question.id,
            selected_option='A',
            is_marked_for_review=True,
            is_visited=True
        )
        self.assertTrue(success)
        first_ans.refresh_from_db()
        self.assertEqual(first_ans.selected_option, 'A')
        self.assertTrue(first_ans.is_marked_for_review)

    def test_evaluation_and_category_benchmarks(self):
        """Tests score calculation and Category 1, 2, 3 thresholds."""
        attempt, _ = start_or_resume_exam_attempt(self.student, self.domain1)
        answers = attempt.answers.all()

        # Simulate 45 correct answers (45 * 2 = 90 marks -> Category 1)
        for idx, ans in enumerate(answers):
            if idx < 45:
                ans.selected_option = ans.question.correct_option
            else:
                ans.selected_option = "D" if ans.question.correct_option != "D" else "C"
            ans.save()

        finalized = evaluate_and_finalize_attempt(attempt)
        self.assertTrue(finalized.is_submitted)
        self.assertEqual(finalized.correct_answers, 45)
        self.assertEqual(finalized.total_score, 90.0)
        self.assertEqual(finalized.percentage, 90.0)
        self.assertEqual(finalized.performance_category, 'CATEGORY_1')
        self.assertIn("Category 1", finalized.category_title)

    def test_proctoring_incident_logging_api(self):
        """Tests real-time browser proctoring incident telemetry recording."""
        attempt, _ = start_or_resume_exam_attempt(self.student, self.domain1)
        
        response = self.client.post(
            reverse('log_incident'),
            data='{"session_token": "' + str(attempt.session_token) + '", "incident_type": "TAB_SWITCH", "details": "Switched to tab 2"}',
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(attempt.proctoring_incidents.count(), 1)
        incident = attempt.proctoring_incidents.first()
        self.assertEqual(incident.incident_type, 'TAB_SWITCH')

    def test_consolidated_excel_report_generation(self):
        """Tests openpyxl consolidated report generation with 13 required columns."""
        attempt, _ = start_or_resume_exam_attempt(self.student, self.domain1)
        evaluate_and_finalize_attempt(attempt)

        excel_buf = generate_consolidated_excel_report()
        self.assertIsNotNone(excel_buf)
        
        # Verify openpyxl can load it and check columns
        wb = load_workbook(filename=excel_buf)
        ws = wb.active
        self.assertEqual(ws["A1"].value, "KORLANCE PRIVATE LIMITED")
        self.assertEqual(ws.max_column, 13)
        self.assertEqual(ws.cell(row=4, column=1).value, "Student Name")
        self.assertEqual(ws.cell(row=4, column=13).value, "Performance Category")

    def test_pdf_score_certificate_generation(self):
        """Tests ReportLab PDF score certificate generation."""
        attempt, _ = start_or_resume_exam_attempt(self.student, self.domain1)
        evaluate_and_finalize_attempt(attempt)

        pdf_buf = generate_result_pdf(attempt)
        self.assertIsNotNone(pdf_buf)
        content = pdf_buf.getvalue()
        # PDF files begin with %PDF
        self.assertTrue(content.startswith(b'%PDF'))

    def test_excel_roster_parsing_and_validation(self):
        """Tests uploading an Excel sheet of students and validating duplicate/invalid entries."""
        wb = Workbook()
        ws = wb.active
        ws.append(["Student Name", "Mobile Number", "Email ID", "Selected Domain"])
        ws.append(["Alice Smith", "9123456780", "alice@example.com", "Artificial Intelligence & Machine Learning (AI & ML)"])
        ws.append(["Bob Invalid", "invalid-phone", "bob-no-email", "NonExistentDomain"])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        result = parse_student_excel_roster(buf)
        self.assertTrue(result['success'])
        self.assertEqual(result['valid_count'], 1)
        self.assertEqual(result['invalid_count'], 1)
        self.assertEqual(result['records'][0]['name'], "Alice Smith")
        self.assertEqual(result['records'][0]['domain_name'], self.domain1.name)
