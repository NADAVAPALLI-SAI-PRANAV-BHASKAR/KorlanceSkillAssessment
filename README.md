# KORLANCE – ENTERPRISE-GRADE MULTI-DOMAIN ONLINE EXAMINATION & PROCTORED ASSESSMENT PLATFORM

> **Official Assessment Platform of KORLANCE PRIVATE LIMITED**  
> *"BUILD TODAY, LEAD TOMORROW."*

---

## 🏛️ Executive Overview

The **KORLANCE Online Examination & Proctored Assessment Platform** is a production-grade enterprise SaaS web application engineered to conduct large-scale, high-integrity technical diagnostic evaluations across **20 industrial engineering and corporate disciplines**.

Designed strictly to enterprise MNC standards, the platform eliminates amateur templates and provides an integrated ecosystem featuring:
- **Client-side & Server-enforced Security:** Real-time online proctoring, webcam identity tracking, tab-switch and focus-loss telemetry logging, server-side timer enforcement (40 minutes), and duplicate-submission locks.
- **Deep Academic Rigor:** Complete 1,000-question domain-specific question bank across 20 distinct technical tracks (50 questions per domain, strictly apportioned into 15 Easy, 25 Medium, and 10 Hard difficulty benchmarks).
- **Automated Instant Evaluation:** Instantaneous server-side score calculation (100 maximum marks), performance merit category classification (Category 1, Category 2, Category 3), automated candidate completion emails, and ReportLab PDF score certificates.
- **Executive Administration Suite:** Searchable candidate roster, drag-and-drop Excel candidate roster ingestion (`.xlsx` / `.xls`), bulk personalized examination invitation dispatches, real-time proctoring telemetry audit, and formatted openpyxl consolidated Excel reporting delivered directly to the corporate administrator (`Shaikbaji15102002@gmail.com`).

---

## 🎨 Brand Identity & Design System

The platform strictly embodies the corporate brand identity of **KORLANCE PRIVATE LIMITED**:
- **Primary Purple:** `#5213B3`
- **Deep Purple:** `#400C92`
- **Accent Lavender:** `#A855F7`
- **Light Lavender:** `#F3EAFE`
- **Background:** `#F8F7FC`
- **Main Text:** `#211A2E`
- **Secondary Text:** `#777184`
- **Typography:** *Plus Jakarta Sans* / *Inter* via Google Fonts CDN.
- **Official Brand Mark:** Geometric K monogram in gradient squircle `#400C92` &rarr; `#5213B3` &rarr; `#7928CA` with crisp wordmark and corporate tagline displayed across all student portals, examination rooms, admin dashboards, email dispatches, and PDF score certificates.

---

## 📂 Project Architecture & Folder Structure

```
c:\SkillAssessmentKorlance\
│
├── korlance_assessment/         # Django Project Root Configuration
│   ├── __init__.py
│   ├── settings.py             # Enterprise settings, database, email, brand constants
│   ├── urls.py                 # Master routing and URL patterns
│   ├── wsgi.py                 # WSGI production server entry point
│   └── asgi.py                 # ASGI asynchronous entry point
│
├── core/                        # Core Global Module
│   ├── context_processors.py   # Global brand tokens injected into all templates
│   ├── views.py                # Public landing page and curriculum overview
│   └── tests.py                # Comprehensive 10-point automated test suite
│
├── accounts/                    # Administrator Authentication Module
│   ├── views.py                # Dedicated MNC admin login & logout
│   └── urls.py
│
├── domains/                     # Domain Taxonomy Module (20 Disciplines)
│   ├── models.py               # Domain model (name, slug, badge, icon, active)
│   └── admin.py
│
├── questions/                   # Question Bank Engine (1,000 MCQs)
│   ├── models.py               # Question model (domain, stem, 4 options, key, difficulty)
│   ├── admin.py
│   └── management/commands/
│       ├── seed_domains_and_questions.py  # Automated 1,000-question database seeder
│       └── question_generator_data.py     # Authentic curriculum question generators
│
├── examinations/                # Candidate Assessment Engine
│   ├── models.py               # Student, ExamInvitation, ExamAttempt, StudentAnswer, CandidateDeclaration
│   ├── views.py                # Registration, instructions, live exam room, save answer API, submit
│   ├── services.py             # 40-min session generation, continuous autosave, server evaluation
│   └── admin.py
│
├── proctoring/                  # Online Proctoring Telemetry Module
│   ├── models.py               # ProctoringIncident model (tab switch, window blur, camera alerts)
│   ├── views.py                # Asynchronous telemetry ingestion endpoint (/proctoring/log-incident/)
│   └── admin.py
│
├── results/                     # Post-Assessment Score & Certification Module
│   ├── views.py                # Dynamic scorecard view, category badge popup
│   └── services.py             # ReportLab vector PDF score certificate generator
│
├── email_service/               # Corporate SMTP Gateway Module
│   ├── models.py               # EmailLog audit model, SMTPSettings configuration
│   ├── services.py             # Dispatches invitations, completion receipts, and consolidated Excel reports
│   └── admin.py
│
├── admin_dashboard/             # Executive Controller Management Suite
│   ├── views.py                # KPI dashboard, roster, Excel import, invitations, proctoring review
│   └── services.py             # OpenPyXL consolidated report generator & roster parser
│
├── static/                      # Static Assets
│   ├── css/
│   │   └── korlance.css        # Enterprise design tokens, palette colors, webcam styles
│   ├── js/
│   │   ├── exam_engine.js      # Palette synchronization, autosave, 40-min countdown timer
│   │   └── proctoring.js       # Camera access, canvas brightness monitor, tab-switch tracking
│   └── images/
│       ├── korlance_logo.svg   # Official vector corporate logo
│       ├── korlance_mark.svg   # Official vector brand monogram
│       └── korlance_logo.png   # High-resolution raster logo for PDF & email clients
│
├── templates/                   # Semantic HTML5 Templates
│   ├── base.html               # Enterprise base shell with brand navbar & footer
│   ├── core/landing.html       # Landing view with 20 domains, rules, and FAQs
│   ├── examinations/
│   │   ├── register.html       # Candidate registration (domain selection/locking)
│   │   ├── instructions.html   # Testing rules & mandatory declaration checkbox
│   │   └── exam_room.html      # 40-min exam workspace, webcam feed, 50-item palette
│   ├── results/
│   │   └── results_view.html   # Scorecard, category popup card, PDF download
│   ├── accounts/
│   │   └── admin_login.html    # Dedicated administrator sign-in page
│   ├── admin_dashboard/
│   │   ├── base_admin.html     # Admin layout with sticky navigation sidebar
│   │   ├── dashboard.html      # Executive KPI cards & Chart.js visualizations
│   │   ├── students_list.html  # Searchable & filterable candidate roster
│   │   ├── excel_upload.html   # Drag-and-drop Excel roster ingestion with pre-import validation
│   │   ├── invitations_list.html # Batch invitation delivery engine
│   │   ├── email_logs.html     # SMTP dispatch audit log
│   │   ├── proctoring_list.html# Real-time proctoring security violation stream
│   │   ├── question_bank.html  # Question bank CRUD interface
│   │   └── smtp_settings.html  # SMTP gateway configuration
│   └── email_service/
│       ├── invitation_email.html # Official invitation template
│       ├── completion_email.html # Official submission receipt template
│       └── admin_report_email.html # Consolidated Excel report dispatch template
│
├── sample_candidates_roster.xlsx # Ready-to-upload candidate Excel sample
├── requirements.txt             # Pip dependency manifest
├── .env                         # Local environment configuration
└── manage.py                    # Django CLI entrypoint
```

---

## 🎯 20 Technical Domains & Question Bank Breakdown

The platform hosts exactly **50 multiple-choice questions per domain**, totaling **1,000 questions**:
1. **Artificial Intelligence & Machine Learning (AI & ML)**
2. **UI/UX Design**
3. **Full Stack Web Development**
4. **Mobile App Development (iOS/Android)**
5. **Cloud Computing**
6. **Cyber Security**
7. **Data Science & Analytics**
8. **Finance & FinTech**
9. **Project Management**
10. **Business Management**
11. **AutoCAD**
12. **Agriculture Technology**
13. **Medical Coding**
14. **Hybrid Vehicles**
15. **Embedded Systems**
16. **VLSI Design**
17. **Digital Marketing**
18. **Python with Data Science**
19. **Python with Machine Learning**
20. **Human Resources**

### Difficulty Benchmark Distribution per Domain:
- **Easy:** 15 Questions (Foundational principles, core definitions, basic syntax)
- **Medium:** 25 Questions (Architectural trade-offs, practical implementation, diagnostic scenarios)
- **Hard:** 10 Questions (Advanced mathematical formulations, edge cases, deep concurrency/timing)
- **Total:** 50 Questions per Domain &times; 2 Marks = **100 Maximum Marks**.

---

## ⏱️ Examination Engine & Question Palette Mechanics

The examination room (`/exam/<session_token>/`) runs a client-side navigation engine (`KorlanceExamEngine`) synchronized with server timestamps:
- **Duration:** Strictly **40 Minutes (2,400 seconds)**.
- **Server Timer Synchronization:** Expiration timestamps are stored in `ExamAttempt.expires_at`. Refreshing the browser or navigating away will not pause or reset the timer.
- **Question Palette Legend:**
  - 🟢 **Green (`.status-answered`):** Question answered.
  - 🔴 **Red (`.status-unanswered`):** Visited, but not answered.
  - 🟣 **Purple (`.status-review`):** Marked for review.
  - ⚪ **Grey (`.status-unvisited`):** Not visited.
  - 🟢🟣 **Green with Purple Ring (`.status-answered-review`):** Answered and marked for review.
- **Continuous Autosave:** Radio button selections trigger asynchronous background saves to `/exam/save-answer/`.
- **Pre-Submission Confirmation:** Clicking *Submit Exam* opens a confirmation modal displaying the count of answered, unanswered, and review-flagged questions.

---

## 🛡️ Online Proctoring System

The browser proctoring engine (`KorlanceProctor`) enforces testing integrity:
1. **Webcam Feed & Face Presence:** Video stream is captured using `navigator.mediaDevices.getUserMedia`. Canvas frame analysis monitors luminosity and camera obstruction.
2. **Tab Switching Detection:** Subscribes to `document.visibilitychange`. If the candidate switches tabs or minimizes the window, an incident is immediately logged.
3. **Window Blur Tracking:** Subscribes to `window.blur` to track focus loss to background tools.
4. **Fullscreen Monitoring:** Subscribes to `fullscreenchange`.
5. **Key Combination Interception:** Intercepts `F12`, `Ctrl+C`, `Ctrl+V`, and right-click context menus.
6. **Telemetry API:** Telemetry events are posted asynchronously to `/proctoring/log-incident/` and cataloged in the `ProctoringIncident` model for controller audit.

---

## 🏆 Performance Merit Categories

Evaluation is instantaneous upon exam submission:
- **Category 1 – Excellent (86–100 Marks):**
  *"Congratulations! You have demonstrated excellent knowledge and understanding of your selected domain."*
- **Category 2 – Good (71–85 Marks):**
  *"Great work! You have a good understanding of your domain. Keep improving your skills."*
- **Category 3 – Needs Improvement (0–70 Marks):**
  *"Keep learning and practising. Strengthen your fundamentals and continue improving your domain knowledge."*

Prominently displayed to all candidates:
> **"Thank you for attending the KORLANCE assessment. Our team will reach you shortly regarding the next steps."**

---

## 📊 Consolidated Excel Reporting & Email Automation

The platform features end-to-end data processing with `openpyxl`:
1. **13-Column Consolidated Excel Report:**
   - 1. Student Name
   - 2. Mobile Number
   - 3. Email ID
   - 4. Selected Domain
   - 5. Examination Status (Completed / In Progress / Pending)
   - 6. Examination Date
   - 7. Total Questions (50)
   - 8. Correct Answers
   - 9. Incorrect Answers
   - 10. Unanswered Questions
   - 11. Marks Obtained (out of 100)
   - 12. Percentage
   - 13. Performance Category
   *Formatted with corporate KORLANCE purple headers (`#5213B3`), zebra striping, and category color pills.*
2. **Email Destination:**
   - Pre-configured to deliver consolidated reports to: **`Shaikbaji15102002@gmail.com`**
   - Editable anytime via the admin panel at `/admin-portal/smtp/`.
3. **Automated Completion Receipts:** Sent immediately upon candidate submission via SMTP.

---

## 🚀 Step-by-Step Local Setup & Execution

### 1. Prerequisites
- Python 3.10+ installed.
- Git.

### 2. Activate Virtual Environment & Install Dependencies
```bash
cd c:\SkillAssessmentKorlance
pip install -r requirements.txt
```

### 3. Initialize Database & Seed 1,000 Questions
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_domains_and_questions
```

### 4. Create Administrator Account
*(Pre-configured default credentials)*
- **Username:** `admin`
- **Email:** `Shaikbaji15102002@gmail.com`
- **Password:** `KorlanceAdmin2026!`

To create an alternate superuser:
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
- **Student Assessment Portal:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Executive Admin Portal:** [http://127.0.0.1:8000/admin-portal/](http://127.0.0.1:8000/admin-portal/)
- **Standard Django Admin:** [http://127.0.0.1:8000/django-admin/](http://127.0.0.1:8000/django-admin/)

---

## 🧪 Automated Test Suite

To run the full 10-point test suite covering domain counts, registration, invitation token locks, continuous autosave, 40-minute timer calculation, category scoring, proctoring telemetry, openpyxl reporting, and ReportLab PDF generation:
```bash
python manage.py test core
```
*Output: `Ran 10 tests in 4.334s ... OK`*

---

## 🚢 Production Deployment Instructions

### 1. Environment Configuration (`.env`)
```ini
DEBUG=False
DJANGO_SECRET_KEY=generate_a_secure_random_50_char_string
ALLOWED_HOSTS=assessment.korlance.com,your-server-ip

# SMTP Production Gateway
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_corporate_email@korlance.com
EMAIL_HOST_PASSWORD=your_16_digit_app_password
DEFAULT_FROM_EMAIL=KORLANCE Assessments <assessments@korlance.com>
ADMIN_REPORT_EMAIL=Shaikbaji15102002@gmail.com
```

### 2. Static Asset Compilation
```bash
python manage.py collectstatic --noinput
```

### 3. WSGI Server Execution (Gunicorn)
```bash
gunicorn korlance_assessment.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

### 4. Nginx Reverse Proxy Configuration
```nginx
server {
    listen 80;
    server_name assessment.korlance.com;

    location /static/ {
        alias /var/www/korlance/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/korlance/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔒 Confidentiality & Security Notice

This assessment infrastructure and all question banks are the proprietary property of **KORLANCE PRIVATE LIMITED**. All examination attempts are digitally audited and subject to automated proctoring review.

**BUILD TODAY. LEAD TOMORROW.**
