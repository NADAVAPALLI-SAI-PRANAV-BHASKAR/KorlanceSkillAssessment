#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install production dependencies
pip install -r requirements.txt

# Collect static files with WhiteNoise
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Seed 20 domains and 1,000 domain-specific MCQs
python manage.py seed_domains_and_questions

# Create default executive administrator account if not present
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'korlance_assessment.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'Shaikbaji15102002@gmail.com', 'KorlanceAdmin2026!')
    print('Executive admin account created.')
"
