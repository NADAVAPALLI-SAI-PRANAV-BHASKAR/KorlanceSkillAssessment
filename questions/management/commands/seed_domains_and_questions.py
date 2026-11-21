from django.core.management.base import BaseCommand
from domains.models import Domain
from questions.models import Question
from django.db import transaction

DOMAINS_DATA = [
    {
        "name": "Artificial Intelligence & Machine Learning (AI & ML)",
        "code": "ai-ml",
        "badge": "Cutting Edge",
        "icon_name": "cpu",
        "description": "Supervised, unsupervised, reinforcement learning, neural networks, computer vision, and NLP architectures."
    },
    {
        "name": "UI/UX Design",
        "code": "ui-ux-design",
        "badge": "Creative SaaS",
        "icon_name": "layout",
        "description": "User research, wireframing, high-fidelity prototyping, design systems, typography, and usability heuristics."
    },
    {
        "name": "Full Stack Web Development",
        "code": "full-stack-web-development",
        "badge": "Enterprise Core",
        "icon_name": "globe",
        "description": "Modern frontend frameworks, backend APIs, relational & NoSQL databases, RESTful architecture, and CI/CD."
    },
    {
        "name": "Mobile App Development (iOS/Android)",
        "code": "mobile-app-development",
        "badge": "High Demand",
        "icon_name": "smartphone",
        "description": "Native and cross-platform mobile engineering with Flutter, React Native, Swift, Kotlin, and offline synchronization."
    },
    {
        "name": "Cloud Computing",
        "code": "cloud-computing",
        "badge": "Infrastructure",
        "icon_name": "cloud",
        "description": "AWS, Azure, GCP infrastructure, virtualization, containerization with Docker & Kubernetes, and serverless compute."
    },
    {
        "name": "Cyber Security",
        "code": "cyber-security",
        "badge": "Information Sec",
        "icon_name": "shield",
        "description": "Network security, cryptography, vulnerability assessment, penetration testing, threat modeling, and SOC operations."
    },
    {
        "name": "Data Science & Analytics",
        "code": "data-science-analytics",
        "badge": "Analytical",
        "icon_name": "bar-chart",
        "description": "Statistical inference, exploratory data analysis, data wrangling, hypothesis testing, SQL, and business intelligence."
    },
    {
        "name": "Finance & FinTech",
        "code": "finance-fintech",
        "badge": "Corporate Finance",
        "icon_name": "dollar-sign",
        "description": "Financial modeling, valuation methods, algorithmic trading, payment gateways, blockchain, and regulatory compliance."
    },
    {
        "name": "Project Management",
        "code": "project-management",
        "badge": "Agile & Delivery",
        "icon_name": "check-square",
        "description": "Agile Scrum, Kanban, waterfall methodologies, scope management, critical path analysis, and risk mitigation."
    },
    {
        "name": "Business Management",
        "code": "business-management",
        "badge": "Strategy & Ops",
        "icon_name": "briefcase",
        "description": "Strategic planning, operations management, organizational behavior, market positioning, and corporate governance."
    },
    {
        "name": "AutoCAD",
        "code": "autocad",
        "badge": "Engineering Design",
        "icon_name": "pen-tool",
        "description": "2D drafting, 3D modeling, parametric constraints, layer standards, geometric dimensioning, and tolerancing (GD&T)."
    },
    {
        "name": "Agriculture Technology",
        "code": "agriculture-technology",
        "badge": "AgriTech",
        "icon_name": "feather",
        "description": "Precision farming, IoT sensor networks, hydroponics, drone surveillance, GIS mapping, and automated irrigation."
    },
    {
        "name": "Medical Coding",
        "code": "medical-coding",
        "badge": "Healthcare IT",
        "icon_name": "activity",
        "description": "ICD-10-CM, CPT, HCPCS coding standards, HIPAA compliance, healthcare reimbursement, and medical necessity audits."
    },
    {
        "name": "Hybrid Vehicles",
        "code": "hybrid-vehicles",
        "badge": "Automotive EV",
        "icon_name": "battery-charging",
        "description": "HEV/PHEV/BEV powertrain dynamics, regenerative braking, battery management systems (BMS), and inverter electronics."
    },
    {
        "name": "Embedded Systems",
        "code": "embedded-systems",
        "badge": "Hardware Engineering",
        "icon_name": "hard-drive",
        "description": "Microcontrollers (ARM Cortex, AVR), RTOS scheduling, device drivers, I2C, SPI, UART, and low-power optimization."
    },
    {
        "name": "VLSI Design",
        "code": "vlsi-design",
        "badge": "Semiconductor",
        "icon_name": "zap",
        "description": "CMOS logic, Verilog/VHDL RTL synthesis, static timing analysis (STA), FPGA prototyping, and ASIC physical design."
    },
    {
        "name": "Digital Marketing",
        "code": "digital-marketing",
        "badge": "Growth & Media",
        "icon_name": "trending-up",
        "description": "SEO strategies, PPC advertising, conversion rate optimization, Google Analytics 4, email funnels, and social attribution."
    },
    {
        "name": "Python with Data Science",
        "code": "python-with-data-science",
        "badge": "Applied Analytics",
        "icon_name": "database",
        "description": "Pandas DataFrame operations, NumPy vectorization, SciPy statistical tests, Matplotlib/Seaborn, and data pipelines."
    },
    {
        "name": "Python with Machine Learning",
        "code": "python-with-machine-learning",
        "badge": "Intelligent Systems",
        "icon_name": "terminal",
        "description": "Scikit-Learn estimators, pipeline transformers, hyperparameter tuning, model persistence, PyTorch, and TensorFlow."
    },
    {
        "name": "Human Resources",
        "code": "human-resources",
        "badge": "People & Culture",
        "icon_name": "users",
        "description": "Talent acquisition, performance appraisal frameworks, labor law compliance, compensation structuring, and HR analytics."
    }
]

class Command(BaseCommand):
    help = "Seeds all 20 official domains and populates exactly 50 authentic MCQs per domain (1,000 total questions)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting seeding of 20 domains and 1,000 MCQs..."))
        
        with transaction.atomic():
            # 1. Create or update domains
            domain_objs = {}
            for item in DOMAINS_DATA:
                domain, created = Domain.objects.update_or_create(
                    code=item["code"],
                    defaults={
                        "name": item["name"],
                        "badge": item["badge"],
                        "icon_name": item["icon_name"],
                        "description": item["description"],
                        "is_active": True
                    }
                )
                domain_objs[item["code"]] = domain
                action = "Created" if created else "Updated"
                self.stdout.write(f"  [{action}] Domain: {domain.name}")

            # 2. Generate questions for each domain
            from .question_generator_data import generate_domain_questions
            
            total_added = 0
            for item in DOMAINS_DATA:
                domain = domain_objs[item["code"]]
                # Check current count
                existing = Question.objects.filter(domain=domain).count()
                if existing < 50:
                    needed = 50 - existing
                    # Delete and reseed cleanly to ensure exact difficulty distribution
                    Question.objects.filter(domain=domain).delete()
                    questions_data = generate_domain_questions(item["code"], item["name"])
                    
                    created_count = 0
                    for q in questions_data:
                        Question.objects.create(
                            domain=domain,
                            question_text=q["text"],
                            option_a=q["options"][0],
                            option_b=q["options"][1],
                            option_c=q["options"][2],
                            option_d=q["options"][3],
                            correct_option=q["correct"],
                            difficulty=q["difficulty"],
                            marks=2,
                            explanation=q["explanation"],
                            is_active=True
                        )
                        created_count += 1
                    total_added += created_count
                    self.stdout.write(self.style.SUCCESS(f"  Successfully seeded 50 questions for '{domain.name}'."))
                else:
                    self.stdout.write(f"  '{domain.name}' already has {existing} questions.")

        total_questions = Question.objects.count()
        self.stdout.write(self.style.SUCCESS(f"\nSeeding complete! Total questions across all domains: {total_questions} (Goal: 1000)."))
