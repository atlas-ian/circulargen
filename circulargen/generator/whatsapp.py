# generator/whatsapp.py

from twilio.rest import Client

def send_whatsapp_message(message, recipients):
    # Twilio configuration (replace these with your actual credentials)
    account_sid = "YOUR_TWILIO_ACCOUNT_SID"
    auth_token = "YOUR_TWILIO_AUTH_TOKEN"
    from_whatsapp_number = 'whatsapp:+YOUR_TWILIO_WHATSAPP_NUMBER'
    
    client = Client(account_sid, auth_token)
    
    # Iterate over recipient phone numbers (format: '+1234567890')
    for recipient in recipients:
        try:
            message_instance = client.messages.create(
                body=message,
                from_=from_whatsapp_number,
                to=f'whatsapp:{recipient}'
            )
            print(f"Message sent to {recipient}: SID {message_instance.sid}")
        except Exception as e:
            print(f"Error sending message to {recipient}: {e}")

