from django.shortcuts import render
from django.http import HttpResponse
from transformers import pipeline

# Initialize the Hugging Face text generation pipeline (using GPT-2 for now)
text_generator = pipeline('text-generation', model='gpt2')

def index(request):
    return render(request, 'generator/index.html')

def generate_circular(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        audience = request.POST.get('audience')
        urgency = request.POST.get('urgency')
        additional_info = request.POST.get('additional_info')

        # Define static official elements (these can later be moved to a settings file or database)
        college_info = "XYZ College\n123 University Road, City, Country\nPhone: +1-234-567-890"
        approved_sign = "Approved by: Dr. John Doe, Principal\nOfficial Seal"
        
        # Create an enhanced prompt including the college header
        prompt = (
            f"{college_info}\n\n"
            f"------------------------------\n"
            f"OFFICIAL CIRCULAR\n"
            f"------------------------------\n"
            f"Subject: {subject}\n"
            f"Audience: {audience}\n"
            f"Urgency: {urgency}\n"
            f"Details: {additional_info}\n\n"
            f"Please draft the circular content in a formal and clear manner. "
            f"Ensure that the text adheres to the style of official college communications.\n\n"
            f"Circular Content:\n"
        )

        # Generate text using the Hugging Face pipeline
        generated = text_generator(prompt, max_length=300, num_return_sequences=1)
        circular_content = generated[0]['generated_text']
        
        # Append the official approved signature
        circular_text = f"{circular_content}\n\n{approved_sign}"

        context = {
            'college_info': college_info,
            'subject': subject,
            'audience': audience,
            'urgency': urgency,
            'additional_info': additional_info,
            'circular': circular_text,
        }
        return render(request, 'generator/result.html', context)
    else:
        return HttpResponse("Invalid Request", status=400)


# Add at the top of views.py
from .whatsapp import send_whatsapp_message

def send_whatsapp(request):
    # For now, we'll use a hardcoded list of recipients.
    # In production, these should come from your database or user input.
    recipients = ['+918123183562']
    
    # For the message, you could send a summary of the circular or a notification.
    message = "A new official circular has been generated. Please check your email or the official portal for details."
    
    send_whatsapp_message(message, recipients)
    
    return HttpResponse("WhatsApp messages triggered successfully!")
