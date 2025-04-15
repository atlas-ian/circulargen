# GenCircular • AI‑Driven Official Circular Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 🚀 Introduction

**GenCircular** is an open‑source Django + React application that automates the creation, formatting, and distribution of official circulars for academic and corporate environments. Leveraging Google’s Gemini generative AI and WeasyPrint PDF rendering, GenCircular transforms minimal user inputs into polished, professional documents—streamlining workflows and ensuring consistency.

---

## 🎯 Aim

- **Automate** drafting of formal circulars with minimal manual effort  
- **Standardize** tone, structure, and formatting across all communications  
- **Integrate** seamless PDF generation and email distribution  
- **Enhance** operational efficiency in institutions and organizations  

---

## 🛠️ Technologies Used

| Layer          | Technology                         |
| -------------- | ---------------------------------- |
| Backend        | Django, Python 3.13                |
| AI Integration | Google Gemini API (generativeai)   |
| PDF Generation | WeasyPrint                         |
| Frontend       | React, Bootstrap 4, Animate.css    |
| Scripting      | jQuery, Bootstrap Datepicker       |
| Email Delivery | Django `EmailMessage` (SMTP)       |

---

## ⚙️ Installation & Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/GenCircular.git
   cd GenCircular
   # Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate.bat

pip install -r requirements.txt
GOOGLE_API_KEY=your_gemini_api_key
DJANGO_SECRET_KEY=your_django_secret_key
EMAIL_HOST_USER=your_smtp_username
EMAIL_HOST_PASSWORD=your_smtp_password


python manage.py migrate
python manage.py createsuperuser


python manage.py collectstatic


python manage.py runserver

Access the app

Admin: http://127.0.0.1:8000/admin/

Generator: http://127.0.0.1:8000/


