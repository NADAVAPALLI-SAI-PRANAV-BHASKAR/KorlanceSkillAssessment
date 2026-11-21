import io
import re
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from django.utils import timezone
from examinations.models import Student, ExamAttempt, ExamInvitation
from domains.models import Domain

def generate_consolidated_excel_report(domain_filter=None, status_filter=None):
    """
    Generates a beautifully styled, enterprise-grade consolidated assessment Excel report.
    Columns:
    1. Student Name
    2. Mobile Number
    3. Email ID
    4. Selected Domain
    5. Examination Status
    6. Examination Date
    7. Total Questions
    8. Correct Answers
    9. Incorrect Answers
    10. Unanswered Questions
    11. Marks Obtained
    12. Percentage
    13. Performance Category
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Assessment Results"
    ws.views.sheetView[0].showGridLines = True

    # Palette
    purple_fill = PatternFill(start_color="5213B3", end_color="5213B3", fill_type="solid")
    dark_purple_fill = PatternFill(start_color="400C92", end_color="400C92", fill_type="solid")
    light_lavender_fill = PatternFill(start_color="F3EAFE", end_color="F3EAFE", fill_type="solid")
    zebra_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    cat1_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    cat2_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    cat3_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")

    font_white_title = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    font_white_sub = Font(name="Calibri", size=10, italic=True, color="E9D5FF")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_data = Font(name="Calibri", size=10, color="211A2E")
    font_data_bold = Font(name="Calibri", size=10, bold=True, color="211A2E")

    thin_border = Border(
        left=Side(style='thin', color='E5E7EB'),
        right=Side(style='thin', color='E5E7EB'),
        top=Side(style='thin', color='E5E7EB'),
        bottom=Side(style='thin', color='E5E7EB')
    )

    # 1. Company Header Banner
    ws.merge_cells("A1:M1")
    title_cell = ws["A1"]
    title_cell.value = "KORLANCE PRIVATE LIMITED"
    title_cell.font = font_white_title
    title_cell.fill = dark_purple_fill
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    ws.merge_cells("A2:M2")
    sub_cell = ws["A2"]
    sub_cell.value = f"CONSOLIDATED ONLINE EXAMINATION RESULTS REPORT — GENERATED {timezone.now().strftime('%d %B %Y, %I:%M %p')}"
    sub_cell.font = font_white_sub
    sub_cell.fill = purple_fill
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    # 2. Table Column Headers
    headers = [
        "Student Name",
        "Mobile Number",
        "Email ID",
        "Selected Domain",
        "Examination Status",
        "Examination Date",
        "Total Questions",
        "Correct Answers",
        "Incorrect Answers",
        "Unanswered Questions",
        "Marks Obtained",
        "Percentage",
        "Performance Category"
    ]

    ws.row_dimensions[4].height = 26
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.font = font_header
        cell.fill = purple_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    # 3. Populate Rows
    students_query = Student.objects.select_related('target_domain').prefetch_related('attempts')
    if domain_filter:
        students_query = students_query.filter(target_domain__id=domain_filter)

    row_idx = 5
    for student in students_query:
        attempt = student.attempts.order_by('-started_at').first()

        status = "Completed" if attempt and attempt.is_submitted else ("In Progress" if attempt else "Pending")
        
        if status_filter:
            if status_filter == 'COMPLETED' and status != 'Completed':
                continue
            if status_filter == 'PENDING' and status != 'Pending':
                continue

        exam_date = attempt.submitted_at.strftime('%Y-%m-%d %H:%M') if attempt and attempt.submitted_at else (attempt.started_at.strftime('%Y-%m-%d %H:%M') if attempt else "N/A")
        total_q = attempt.total_questions if attempt else 50
        correct_a = attempt.correct_answers if attempt and attempt.is_submitted else "-"
        incorrect_a = attempt.incorrect_answers if attempt and attempt.is_submitted else "-"
        unanswered_q = attempt.unanswered_questions if attempt and attempt.is_submitted else "-"
        score = f"{attempt.total_score:.1f} / 100" if attempt and attempt.is_submitted else "-"
        percentage = f"{attempt.percentage:.1f}%" if attempt and attempt.is_submitted else "-"
        
        cat_display = "-"
        cat_code = ""
        if attempt and attempt.is_submitted:
            cat_code = attempt.performance_category
            cat_display = attempt.get_performance_category_display()

        row_values = [
            student.full_name,
            student.mobile_number,
            student.email,
            student.target_domain.name,
            status,
            exam_date,
            total_q,
            correct_a,
            incorrect_a,
            unanswered_q,
            score,
            percentage,
            cat_display
        ]

        ws.row_dimensions[row_idx].height = 20
        is_even = (row_idx % 2 == 0)

        for col_idx, val in enumerate(row_values, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_data
            cell.border = thin_border
            
            # Alignments
            if col_idx in [1, 3, 4]:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Highlighting
            if is_even:
                cell.fill = zebra_fill

            # Category pill highlighting
            if col_idx == 13:
                if cat_code == 'CATEGORY_1':
                    cell.fill = cat1_fill
                    cell.font = font_data_bold
                elif cat_code == 'CATEGORY_2':
                    cell.fill = cat2_fill
                    cell.font = font_data_bold
                elif cat_code == 'CATEGORY_3':
                    cell.fill = cat3_fill
                    cell.font = font_data_bold

        row_idx += 1

    # Auto-fit column widths
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            # Skip merged banner in width calculation
            if cell.row in [1, 2]:
                continue
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    # Save to buffer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def parse_student_excel_roster(file_obj):
    """
    Parses and validates an uploaded Excel sheet (.xlsx/.xls) of candidate applicants.
    Expected columns: Student Name, Mobile Number, Email ID, Selected Domain.
    """
    from openpyxl import load_workbook

    wb = load_workbook(filename=file_obj, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows or len(rows) < 2:
        return {
            'success': False,
            'error': 'Uploaded spreadsheet is empty or missing headers.',
            'records': []
        }

    # Find column indices
    headers = [str(h).strip().lower() if h else '' for h in rows[0]]
    
    name_col = -1
    mobile_col = -1
    email_col = -1
    domain_col = -1

    for idx, h in enumerate(headers):
        if 'name' in h:
            name_col = idx
        elif 'mobile' in h or 'phone' in h or 'contact' in h:
            mobile_col = idx
        elif 'email' in h:
            email_col = idx
        elif 'domain' in h or 'course' in h or 'track' in h:
            domain_col = idx

    if any(col == -1 for col in [name_col, mobile_col, email_col, domain_col]):
        return {
            'success': False,
            'error': 'Required columns missing. Expected: Student Name, Mobile Number, Email ID, Selected Domain.',
            'records': []
        }

    # Build domain map for case-insensitive lookup
    domains = {d.name.lower().strip(): d for d in Domain.objects.filter(is_active=True)}

    parsed_records = []
    seen_emails = set()

    email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    mobile_regex = re.compile(r"^\+?[\d\s-]{10,15}$")

    for row_num, row in enumerate(rows[1:], start=2):
        if not any(row):
            continue

        raw_name = str(row[name_col] or '').strip()
        raw_mobile = str(row[mobile_col] or '').strip()
        raw_email = str(row[email_col] or '').strip().lower()
        raw_domain = str(row[domain_col] or '').strip()

        errors = []
        if not raw_name:
            errors.append("Missing name")
        if not raw_mobile or not mobile_regex.match(raw_mobile):
            errors.append("Invalid mobile number")
        if not raw_email or not email_regex.match(raw_email):
            errors.append("Invalid email address")
        elif raw_email in seen_emails:
            errors.append("Duplicate in file")
        seen_emails.add(raw_email)

        # Match domain
        matched_domain = None
        for d_name_lower, d_obj in domains.items():
            if raw_domain.lower() in d_name_lower or d_name_lower in raw_domain.lower():
                matched_domain = d_obj
                break

        if not matched_domain:
            errors.append(f"Domain '{raw_domain}' not recognized")

        # Check existing in DB
        db_exists = Student.objects.filter(email=raw_email).exists() if raw_email else False

        parsed_records.append({
            'row_num': row_num,
            'name': raw_name,
            'mobile': raw_mobile,
            'email': raw_email,
            'domain_raw': raw_domain,
            'domain_id': matched_domain.id if matched_domain else None,
            'domain_name': matched_domain.name if matched_domain else "Unmatched",
            'is_valid': len(errors) == 0,
            'errors': errors,
            'already_exists': db_exists
        })

    return {
        'success': True,
        'records': parsed_records,
        'valid_count': sum(1 for r in parsed_records if r['is_valid']),
        'invalid_count': sum(1 for r in parsed_records if not r['is_valid']),
        'duplicate_db_count': sum(1 for r in parsed_records if r['already_exists'])
    }
