# generator/views.py

import os
import re

from django.shortcuts       import render, redirect
from django.http            import HttpResponse
from django.template.loader import render_to_string
from django.conf            import settings
from django.contrib         import messages
from django.contrib.auth    import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail       import EmailMessage
import google.generativeai as genai
from weasyprint import HTML

# ─────────────────────────────────────────────────────────────────────────────
# 1. HOD Mapping by Department Code
# ─────────────────────────────────────────────────────────────────────────────
HOD_BY_DEPT = {
    'CSE':   'Dr. Nirmala C R',
    'MECH':  'Dr. G. Manavendra',
    'CIVIL': 'Dr. Chidananda G',
    'EEE':   'Dr. M S Nagaraj',
    'ECE':   'Dr. G.S. Sunitha',
    'ISE':   'Dr. Poornima B',
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Configure Google Gemini AI (if API key present)
# ─────────────────────────────────────────────────────────────────────────────
api_key = getattr(settings, 'GOOGLE_API_KEY', os.environ.get("GOOGLE_API_KEY"))
if api_key:
    genai.configure(api_key=api_key)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Authentication Views
# ─────────────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
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


# ─────────────────────────────────────────────────────────────────────────────
# 4. Main Application Views
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def index(request):
    """
    Renders the form page for generating a circular.
    """
    return render(request, 'generator/index.html')


@login_required
def generate_circular(request):
    """
    Handles form submission:
      1. Collects form data.
      2. Builds and sends prompt to Gemini.
      3. Receives AI-generated circular content.
      4. Renders and saves PDF via WeasyPrint.
      5. Returns the result page with PDF download/send options.
    """
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    # --- 4.1 Collect form inputs ---
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

    # --- 4.2 Determine HOD name from mapping ---
    hod_name = HOD_BY_DEPT.get(department, '')

    # --- 4.3 Build Gemini prompt ---
    prompt = (
        "Write a formal and concise college circular in one paragraph, "
        "no bullets in body. Keep Subject on its own line before details. "
        "After, list Venue, Date, Time as bullets. Do NOT include signatures.\n\n"
        f"Subject: {subject}\n"
        f"Audience: {audience}\n"
        f"Urgency: {urgency}\n"
        f"Agenda: {agenda}\n"
        f"Details: {additional_info}\n\n"
        f"* Venue: {venue}\n"
        f"* Date: {event_datetime.split(',')[0] if ',' in event_datetime else event_datetime}\n"
        f"* Time: {event_datetime.split(',')[-1].strip() if ',' in event_datetime else ''}\n\n"
        "Circular Content:\n"
    )
    model    = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content(prompt)
    circular = re.sub(r'\*\*(.*?)\*\*', r'\1', response.text)

    # --- 4.4 Prepare template context ---
    context = {
        'subject':         subject,
        'audience':        audience,
        'urgency':         urgency,
        'agenda':          agenda,
        'additional_info': additional_info,
        'venue':           venue,
        'event_datetime':  event_datetime,
        'department':      department,
        'hod_name':        hod_name,
        'circular':        circular,
        'date':            date,
        'recipient_email': recipient_email,
        'is_pdf':          False,
    }

    # --- 4.5 Render HTML for PDF (same template) ---
    html_string = render_to_string('generator/result.html', {**context, 'is_pdf': True})
    base_url     = request.build_absolute_uri('/')  # for static file resolution
    pdf_bytes    = HTML(string=html_string, base_url=base_url).write_pdf()

    # --- 4.6 Save PDF to disk ---
    pdf_dir  = os.path.join(settings.BASE_DIR, 'generated_pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_name = f"circular_{subject.replace(' ', '_')}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_name)

    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)

    # --- 4.7 Return result page ---
    context['pdf_filename'] = pdf_name
    return render(request, 'generator/result.html', context)


@login_required
def send_email(request):
    """
    Attaches the generated PDF and emails it to the specified recipients.
    """
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    pdf_filename   = request.POST['pdf_filename']
    raw            = request.POST['recipient_email']
    recipients     = [e.strip() for e in raw.split(',') if e.strip()]
    subject        = request.POST['subject']
    pdf_path       = os.path.join(settings.BASE_DIR, 'generated_pdfs', pdf_filename)

    if not os.path.exists(pdf_path):
        return HttpResponse("PDF not found.", status=404)

    email = EmailMessage(
        subject=f"Circular: {subject}",
        body="Dear recipient,\n\nPlease find attached the official circular.\n\nRegards,\nAdmin Office",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients
    )
    email.attach_file(pdf_path)

    try:
        email.send()
        return render(request, 'generator/email_status.html', {'status': 'success'})
    except Exception:
        return render(request, 'generator/email_status.html', {'status': 'failed'})
