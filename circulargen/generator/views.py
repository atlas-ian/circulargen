# generator/views.py

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
from django.core.mail import EmailMessage
from xhtml2pdf import pisa
import google.generativeai as genai

# ========== 1. CONFIGURE GEMINI API ==========
api_key = getattr(settings, 'GOOGLE_API_KEY', os.environ.get("GOOGLE_API_KEY"))
if api_key:
    genai.configure(api_key=api_key)

# ========== 2. AUTH VIEWS ==========

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
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

    # ---- form inputs ----
    subject         = request.POST['subject']
    date            = request.POST['date']
    audience        = request.POST['audience']
    urgency         = request.POST['urgency']
    agenda          = request.POST['agenda']
    additional_info = request.POST['additional_info']
    # note            = request.POST.get('note', '')
    venue = request.POST.get('venue')
    event_datetime = request.POST.get('event_datetime')
    recipient_email = request.POST['recipient_email']

    # ---- college header ----
    college_info = "Bapuji Institute of Engineering and Technology\nShamnur Road, Davangere-577004, Karnataka, India\n"

    # ---- Gemini prompt ----
    prompt = (
        # f"{college_info}\n\n"
        # "------------------------------\n"
        # "OFFICIAL CIRCULAR\n"
        # "------------------------------\n"
        f"Subject: {subject}\n"
        f"Audience: {audience}\n"
        f"Urgency: {urgency}\n"
        f"Agenda: {agenda}\n"
        f"Details: {additional_info}\n\n"
        f"Venue: {venue}\n"
        f"Event date and time: {event_datetime}\n"
        "Please draft the circular content in a formal and clear manner.\n\n"
        "Circular Content:\n"

    )
    model    = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content(prompt)
    circular = re.sub(r'\*\*(.*?)\*\*', r'\1', response.text)

    # ---- template context ----
    context = {
        # 'college_info': college_info,
        'subject': subject,
        'audience': audience,
        'urgency': urgency,
        'agenda': agenda,
        'additional_info': additional_info,
        'venue': venue,
        'event_datetime': event_datetime,
        'circular': circular,
        'date': date,
        # 'note': note,
        'recipient_email': recipient_email,
        'is_pdf': False,
        'email_sent': None,
    }

    # ---- render & save PDF ----
    pdf_html    = render_to_string('generator/pdf_template.html', {**context, 'is_pdf': True})
    pdf_dir     = os.path.join(settings.BASE_DIR, 'generated_pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_name    = f"circular_{subject.replace(' ', '_')}.pdf"
    pdf_path    = os.path.join(pdf_dir, pdf_name)

    with open(pdf_path, "wb") as f:
        pisa_status = pisa.CreatePDF(io.BytesIO(pdf_html.encode("UTF-8")), dest=f)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    context['pdf_filename'] = pdf_name
    return render(request, 'generator/result.html', context)

# ========== 5. SEND EMAIL (multiple recipients) ==========

@login_required
def send_email(request):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    pdf_filename = request.POST['pdf_filename']
    raw          = request.POST.get('recipient_email', '').strip()
    # parse comma-separated emails
    recipients   = [e.strip() for e in raw.split(',') if e.strip()]
    subject      = request.POST['subject']

    pdf_path = os.path.join(settings.BASE_DIR, 'generated_pdfs', pdf_filename)
    if not os.path.exists(pdf_path):
        return HttpResponse("PDF not found.", status=404)

    # build and send
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
