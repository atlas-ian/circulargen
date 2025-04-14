import google.generativeai as genai
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os
import re

# Configure Gemini API (if API key is available)
if hasattr(settings, 'GOOGLE_API_KEY'):
    genai.configure(api_key=settings.GOOGLE_API_KEY)
elif os.environ.get("GOOGLE_API_KEY"):
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def index(request):
    return render(request, 'generator/index.html')

def generate_circular(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        date = request.POST.get('date')
        agenda = request.POST.get('agenda')
        audience = request.POST.get('audience')
        urgency = request.POST.get('urgency')
        additional_info = request.POST.get('additional_info')
        venue = request.POST.get('venue')
        event_datetime = request.POST.get('event_datetime')
        #note = request.POST.get('note')

        # Define static official elements (these can later be moved to a settings file or database)
        college_info = "Bapuji Institute of Engineering and Technology\nShamnur Road, Davangere-577004, Karnataka, India\n"
        #Phone:91-8192-222245\nhttps://www.bietdvg.edu"
        #approved_sign = "Approved by: Dr. H B Aravind, Principal\nOfficial Seal"
        
        # Create an enhanced prompt including the college header
        prompt = (
            f"Write a formal and concise college circular in a single paragraph format, without unnecessary line breaks or bullet points in the main body. "
            f"The circular should announce the event in a professional tone as practiced in academic institutions. "
            f"Keep the Subject in seperate line before the details.After the paragraph, clearly list the Venue, Date, and Time as separate bullet points. "
            f"End the circular with the signature that is mentioned in the details.\n\n"
            # f"{college_info}\n\n"
            # f"------------------------------\n"
            # f"OFFICIAL CIRCULAR\n"
            # f"------------------------------\n"
            f"Subject: {subject}\n"
            f"Agenda: {agenda}\n"
            f"Audience: {audience}\n"
            #f"Urgency: {urgency}\n"
            f"Details: {additional_info}\n\n"
            f"Venue: {venue}\n"
            f"Event date and time: {event_datetime}\n"
            f"Circular Content:\n"
        )

        # Initialize the Hugging Face text generation pipeline (using GPT-2 for now)
        # text_generator = pipeline('text-generation', model='gpt2')

        # Generate text using the Gemini API
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        circular_content = response.text
        
        # Remove bold symbols using regular expressions
        circular_content = re.sub(r'\\(.?)\\*', r'\1', circular_content)

        # Append the official approved signature
        circular_text = f"{circular_content}\n\n "
        #{approved_sign}

        context = {
            #'college_info': college_info,
            'subject': subject,
            'agenda': agenda,
            'audience': audience,
            'urgency': urgency,
            'additional_info': additional_info,
            'venue': venue,
            'event_datetime': event_datetime,
            'circular': circular_text,
            'date': date,
            # 'note': note,
        }
        return render(request, 'generator/result.html', context)
    else:
        return HttpResponse("Invalid Request", status=400)

# Add at the top of views.py
# from .whatsapp import send_whatsapp_message

# def send_whatsapp(request):
#     # For now, we'll use a hardcoded list of recipients.
#     # In production, these should come from your database or user input.
#     recipients = ['+918123183562']
    
#     # For the message, you could send a summary of the circular or a notification.
#     message = "A new official circular has been generated. Please check your email or the official portal for details."
    
#     send_whatsapp_message(message, recipients)
    
#     return HttpResponse("WhatsApp messages triggered successfully!")