from django.shortcuts import render
from django.http import HttpResponse
from transformers import pipeline

# Create your views here.


# Initialize the Hugging Face text generation pipeline
# (You can fine-tune your own model later; for now, we're using GPT-2 as an example)
text_generator = pipeline('text-generation', model='gpt2')

def index(request):
    return render(request, 'generator/index.html')

def generate_circular(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        audience = request.POST.get('audience')
        urgency = request.POST.get('urgency')
        additional_info = request.POST.get('additional_info')

        # Create a prompt for the model using user inputs
        prompt = (
            f"Official Circular:\n"
            f"Subject: {subject}\n"
            f"Audience: {audience}\n"
            f"Urgency: {urgency}\n"
            f"Details: {additional_info}\n\n"
            "Circular Content:\n"
        )

        # Generate text using the Hugging Face pipeline
        generated = text_generator(prompt, max_length=250, num_return_sequences=1)
        circular_text = generated[0]['generated_text']

        context = {
            'circular': circular_text,
            'subject': subject,
            'audience': audience,
            'urgency': urgency,
            'additional_info': additional_info,
        }
        return render(request, 'generator/result.html', context)
    else:
        return HttpResponse("Invalid Request", status=400)
