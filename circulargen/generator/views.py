# generator/views.py
from weasyprint import HTML

import base64
import os
import re
import io

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from xhtml2pdf import pisa
import google.generativeai as genai

# Mapping of department value → HOD name
HOD_BY_DEPT = {
    'CSE':  'Dr. Nirmala C R',
    'MECH': 'Dr. G. Manavendra',
    'CIVIL':'Dr. Chidananda G',
    'EEE':  'Dr. M S Nagaraj',
    'ECE':  'Dr. G.S. Sunitha',
    'ISE':  'Dr. Poornima B',
}

# ========== 1. CONFIGURE GEMINI API ==========
api_key = getattr(settings, 'GOOGLE_API_KEY', os.environ.get("GOOGLE_API_KEY"))
if api_key:
    genai.configure(api_key=api_key)

# ========== 2. AUTH VIEWS ==========
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'index'))
        messages.error(request, "Invalid credentials")
    return render(request, 'generator/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# ========== 3. INDEX ==========
@login_required
def index(request):
    return render(request, 'generator/index.html')

# ========== 4. GENERATE CIRCULAR & PDF ==========
@login_required
def generate_circular(request):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    # --- Collect form data ---
    subject         = request.POST['subject']
    date            = request.POST['date']
    audience        = request.POST['audience']
    urgency         = request.POST['urgency']
    agenda          = request.POST['agenda']
    additional_info = request.POST['additional_info']
    venue           = request.POST.get('venue', '')
    event_datetime  = request.POST.get('event_datetime', '')
    department      = request.POST['department']
    recipient_email = request.POST['recipient_email']

    # --- Get HOD Name dynamically from input form ---
    # If an input for hod_name is provided, use that. Otherwise, fallback to the mapping.
    hod_name_input = request.POST.get('hod_name', '').strip()
    if hod_name_input:
        hod_name = hod_name_input
    else:
        hod_name = HOD_BY_DEPT.get(department, f"Head, Dept. of {department}")

    # --- Build Gemini prompt ---
    prompt = (
        "Write a formal and concise college circular in a single paragraph format, "
        "without unnecessary line breaks or bullet points in the main body. "
        "Keep the Subject on its own line before the details. "
        "After the paragraph, list Venue, Date, and Time as bullet points. "
        "Do NOT include any signatory lines like the HOD or Principal. They will be added separately in the template.\n\n"
        f"Subject: {subject}\n"
        f"Audience: {audience}\n"
        f"Urgency: {urgency}\n"
        f"Agenda: {agenda}\n"
        f"Details: {additional_info}\n\n"
        f"* Venue: {venue}\n"
        f"* Date: {event_datetime.split(',')[0]}\n"
        f"* Time: {event_datetime.split(',')[-1].strip()}\n\n"
        "Circular Content:\n"
    )

    model    = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content(prompt)
    circular = re.sub(r'\*\*(.*?)\*\*', r'\1', response.text)

    # --- Helper to embed static logos as base64 ---
    def to_data_uri(static_path):
        # finders.find will locate the file under STATICFILES_DIRS or app/static
        full_path = finders.find(static_path)
        if not full_path:
            raise FileNotFoundError(f"Static file not found: {static_path}")
        with open(full_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('ascii')
        ext = os.path.splitext(full_path)[1].lstrip('.').lower()
        return f"data:image/{ext};base64,{encoded}"

    context = {
        'subject': subject,
        'audience': audience,
        'urgency': urgency,
        'agenda': agenda,
        'additional_info': additional_info,
        'venue': venue,
        'event_datetime': event_datetime,
        'department': department,
        'hod_name': hod_name,
        'circular': circular,
        'date': date,
        'recipient_email': recipient_email,
        'is_pdf': False,
        # embed your logos via static finder
        'left_logo_data_uri':  to_data_uri('generator/img/BIET.png'),
        'right_logo_data_uri': to_data_uri('generator/img/VTUlogo.png'),
    }

    # --- Render HTML for PDF ---
    html = render_to_string('generator/pdf_template.html', context)

    # --- Write PDF file with WeasyPrint ---
    pdf_dir  = os.path.join(settings.BASE_DIR, 'generated_pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_name = f"circular_{subject.replace(' ', '_')}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_name)

    HTML(string=html).write_pdf(pdf_path)

    context['pdf_filename'] = pdf_name
    return render(request, 'generator/result.html', context)

# ========== 5. SEND EMAIL ==========
@login_required
def send_email(request):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    pdf_filename = request.POST['pdf_filename']
    raw          = request.POST.get('recipient_email', '')
    recipients   = [e.strip() for e in raw.split(',') if e.strip()]
    subject      = request.POST['subject']

    pdf_path = os.path.join(settings.BASE_DIR, 'generated_pdfs', pdf_filename)
    if not os.path.exists(pdf_path):
        return HttpResponse("PDF not found.", status=404)

    email = EmailMessage(
        subject=f"Circular: {subject}",
        body="Dear recipient,\n\nPlease find attached the official circular.\n\nRegards,\nAdmin Office",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    email.attach_file(pdf_path)

    try:
        email.send()
        return render(request, 'generator/email_status.html', {'status': 'success'})
    except Exception as e:
        print("Email sending error:", e)
        return render(request, 'generator/email_status.html', {'status': 'failed'})
