import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings

def generate_result_pdf(attempt):
    """
    Renders an enterprise official KORLANCE examination score certificate.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#400C92'),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#777184'),
        alignment=1
    )
    header_style = ParagraphStyle(
        'SecHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#5213B3')
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#211A2E')
    )
    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#5213B3'),
        alignment=1
    )

    # 1. Header with Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'korlance_logo.png')
    if os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=280, height=60)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 10))
        except Exception:
            pass

    story.append(Paragraph("OFFICIAL ASSESSMENT PERFORMANCE REPORT", title_style))
    story.append(Paragraph("KORLANCE PRIVATE LIMITED — BUILD TODAY, LEAD TOMORROW.", subtitle_style))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#5213B3'), spaceAfter=15))

    # 2. Candidate Information Table
    student = attempt.student
    cat_display = attempt.get_performance_category_display()
    exam_date = attempt.submitted_at.strftime('%d %B %Y, %I:%M %p') if attempt.submitted_at else "N/A"

    cand_data = [
        [Paragraph("<b>Candidate Name:</b>", body_style), Paragraph(student.full_name, body_style),
         Paragraph("<b>Roll / Attempt ID:</b>", body_style), Paragraph(f"KOR-{attempt.id:06d}", body_style)],
        [Paragraph("<b>Email Address:</b>", body_style), Paragraph(student.email, body_style),
         Paragraph("<b>Mobile Number:</b>", body_style), Paragraph(student.mobile_number, body_style)],
        [Paragraph("<b>Assessed Domain:</b>", body_style), Paragraph(attempt.domain.name, body_style),
         Paragraph("<b>Examination Date:</b>", body_style), Paragraph(exam_date, body_style)]
    ]

    cand_table = Table(cand_data, colWidths=[110, 160, 110, 160])
    cand_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F7FC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F3EAFE')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cand_table)
    story.append(Spacer(1, 15))

    # 3. Score Breakdown
    story.append(Paragraph("ASSESSMENT SCORECARD", header_style))
    story.append(Spacer(1, 8))

    score_data = [
        ["Evaluation Metric", "Benchmark / Max", "Candidate Score"],
        ["Total Multiple Choice Questions", "50 Questions", str(attempt.total_questions)],
        ["Correctly Answered Questions", "50 Questions", str(attempt.correct_answers)],
        ["Incorrect Answers", "—", str(attempt.incorrect_answers)],
        ["Unanswered Questions", "—", str(attempt.unanswered_questions)],
        ["Total Marks Obtained", "100 Marks", f"{attempt.total_score:.1f} / 100"],
        ["Overall Percentage", "100.0%", f"{attempt.percentage:.1f}%"],
    ]

    score_table = Table(score_data, colWidths=[240, 150, 150])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5213B3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 15))

    # 4. Performance Category Card
    cat_banner_color = colors.HexColor('#F3EAFE')
    if attempt.performance_category == 'CATEGORY_1':
        cat_banner_color = colors.HexColor('#DCFCE7')
        cat_desc = "Congratulations! You have demonstrated excellent knowledge and understanding of your selected domain."
    elif attempt.performance_category == 'CATEGORY_2':
        cat_banner_color = colors.HexColor('#FEF3C7')
        cat_desc = "Great work! You have a good understanding of your domain. Keep improving your skills."
    else:
        cat_banner_color = colors.HexColor('#FEE2E2')
        cat_desc = "Keep learning and practising. Strengthen your fundamentals and continue improving your domain knowledge."

    cat_box = [
        [Paragraph(f"<b>QUALIFYING RESULT: {cat_display}</b>", badge_style)],
        [Paragraph(cat_desc, subtitle_style)]
    ]
    cat_table = Table(cat_box, colWidths=[540])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), cat_banner_color),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#A855F7')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 20))

    # 5. Official Verification & Footer
    disclaimer_text = (
        "<b>Notice:</b> This document is an official assessment record issued by KORLANCE PRIVATE LIMITED. "
        "All responses were recorded under verified online proctoring protocols. "
        "Thank you for attending the KORLANCE assessment. Our team will reach you shortly regarding the next steps."
    )
    story.append(Paragraph(disclaimer_text, subtitle_style))
    story.append(Spacer(1, 25))

    footer_data = [
        [Paragraph("<b>Candidate Signature</b><br/><br/>______________________", subtitle_style),
         Paragraph(f"<b>Verification Security Hash:</b><br/>{str(attempt.session_token)[:24]}...<br/>Digitally Certified", subtitle_style),
         Paragraph("<b>Authorized Controller of Examinations</b><br/><br/><b>KORLANCE PRIVATE LIMITED</b>", subtitle_style)]
    ]
    footer_table = Table(footer_data, colWidths=[180, 180, 180])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(footer_table)

    doc.build(story)
    buffer.seek(0)
    return buffer
