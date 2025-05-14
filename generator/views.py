# generator/views.py

import os
import re
import uuid

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
# 1b. Department full-name mapping
# ─────────────────────────────────────────────────────────────────────────────
DEPT_FULL_BY_CODE = {
    'CSE':   'Computer Science and Engineering',
    'MECH':  'Mechanical Engineering',
    'CIVIL': 'Civil Engineering',
    'EEE':   'Electrical & Electronics Engineering',
    'ECE':   'Electronics & Communication Engineering',
    'ISE':   'Information Science & Engineering',
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Signature URLs on GitHub (raw)
# ─────────────────────────────────────────────────────────────────────────────
GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/adarshaadi06/circulargen"
    "/main/generator/static/generator/signatures"
)

HOD_SIG_URLS = {
    'CSE':   "https://github.com/adarshaadi06/circulargen/blob/main/generator/static/generator/signatures/CSE-sign.png?raw=true",
    'MECH':  "https://raw.githubusercontent.com/adarshaadi06/circulargen/main/generator/static/generator/signatures/MECH-sign.png?raw=true",
    'CIVIL': "https://raw.githubusercontent.com/adarshaadi06/circulargen/main/generator/static/generator/signatures/CIVIL-sign.png?raw=true",
    'EEE':   "https://raw.githubusercontent.com/adarshaadi06/circulargen/main/generator/static/generator/signatures/EEE-sign.png?raw=true",
    'ECE':   "https://raw.githubusercontent.com/adarshaadi06/circulargen/main/generator/static/generator/signatures/ECE-sign.png?raw=true",
    'ISE':   "https://raw.githubusercontent.com/adarshaadi06/circulargen/main/generator/static/generator/signatures/ISE-sign.png?raw=true",
}

DIRECTOR_SIG_URL   = f"{GITHUB_RAW_BASE}/director-sign.png?raw=true"
PRINCIPAL_SIG_URL  = f"{GITHUB_RAW_BASE}/principal-sign.png?raw=true"

# ─────────────────────────────────────────────────────────────────────────────
# 3. Configure Google Gemini AI (if API key present)
# ─────────────────────────────────────────────────────────────────────────────
api_key = getattr(settings, 'GOOGLE_API_KEY', os.environ.get("GOOGLE_API_KEY"))
if api_key:
    genai.configure(api_key=api_key)

# ─────────────────────────────────────────────────────────────────────────────
# 4. Authentication Views
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
# 5. Main Application Views
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def index(request):
    return render(request, 'generator/index.html')


@login_required
def generate_circular(request):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    # --- 5.1 Collect form inputs ---
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

    # --- 5.2 HOD name, dept full-name & signature URL ---
    hod_name           = HOD_BY_DEPT.get(department, 'Head of Department')
    dept_full          = DEPT_FULL_BY_CODE.get(department, department)
    hod_signature_url  = HOD_SIG_URLS.get(department, '')

    # --- 5.3 Build AI prompt & generate circular text ---
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

    if api_key == 'DEMO-API-KEY':
        circular = (
            f"Subject: {subject}\n"
            f"This is a simulated circular for {audience} about '{agenda}'. "
            f"Details: {additional_info}.\n"
            f"* Venue: {venue}\n"
            f"* Date: {event_datetime.split(',')[0]}\n"
            f"* Time: {event_datetime.split(',')[-1].strip()}\n"
        )
    else:
        model    = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        circular = re.sub(r'\*\*(.*?)\*\*', r'\1', response.text)

    # --- 5.4 Generate unique Circular ID ---
    circular_id = uuid.uuid4().hex[:8].upper()

    # --- 5.5 Build template context ---
    context = {
        'subject':                subject,
        'audience':               audience,
        'urgency':                urgency,
        'agenda':                 agenda,
        'additional_info':        additional_info,
        'venue':                  venue,
        'event_datetime':         event_datetime,
        'department':             department,
        'dept_full':              dept_full,
        'hod_name':               hod_name,
        'hod_signature_url':      hod_signature_url,
        'director_signature_url': DIRECTOR_SIG_URL,
        'principal_signature_url':PRINCIPAL_SIG_URL,
        'circular':               circular,
        'date':                   date,
        'circular_id':            circular_id,
        'recipient_email':        recipient_email,
        'is_pdf':                 False,
    }

    # --- 5.6 Render PDF bytes ---
    html_string = render_to_string(
        'generator/result.html', {**context, 'is_pdf': True}
    )
    base_url  = request.build_absolute_uri('/')
    pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()

    # --- 5.7 Save PDF to disk ---
    pdf_dir  = os.path.join(settings.BASE_DIR, 'generated_pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_name = f"circular_{subject.replace(' ', '_')}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_name)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)

    # --- 5.8 Return result page ---
    context['pdf_filename'] = pdf_name
    return render(request, 'generator/result.html', context)


@login_required
def send_email(request):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    pdf_filename = request.POST['pdf_filename']
    raw          = request.POST['recipient_email']
    recipients   = [e.strip() for e in raw.split(',') if e.strip()]
    subject      = request.POST['subject']
    pdf_path     = os.path.join(settings.BASE_DIR, 'generated_pdfs', pdf_filename)

    if not os.path.exists(pdf_path):
        return HttpResponse("PDF not found.", status=404)

    email = EmailMessage(
        subject=f"Circular: {subject}",
        body="Dear recipient,\n\nPlease find attached the official circular.\n\nRegards,\nAdmin Office",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients
    )
    email.attach_file(pdf_path)

    status = 'success' if email.send() else 'failed'
    return render(request, 'generator/email_status.html', {'status': status})
