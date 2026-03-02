import os
import resend

api_key = os.getenv("RESEND_API_KEY", "")
from_email = os.getenv("RESEND_FROM_EMAIL", "")
print(f"Resend API Key present: {bool(api_key)}")
print(f"Resend From Email: {from_email}")
print(f"Resend Key prefix: {api_key[:10]}...")

try:
    resend.api_key = api_key
    result = resend.Emails.send({
        "from": from_email,
        "to": "test@example.com",
        "subject": "Test Email from Resend",
        "html": "<p>Test email</p>",
    })
    print(f"Resend result: {result}")
except Exception as e:
    print(f"Resend error: {type(e).__name__}: {e}")
