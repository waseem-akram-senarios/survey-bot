import os
from mailersend import EmailBuilder, MailerSendClient

api_key = os.getenv("MAILERSEND_API_KEY", "")
sender = os.getenv("MAILERSEND_SENDER_EMAIL", "")

print(f"API Key present: {bool(api_key) and not api_key.startswith('<')}")
print(f"Sender: {sender}")
print(f"API Key prefix: {api_key[:10]}...")

try:
    ms = MailerSendClient(api_key=api_key)
    msg = (
        EmailBuilder()
        .from_email(sender, "SurvAI")
        .to_many([{"email": "test@example.com", "name": "Test"}])
        .subject("Test Email")
        .html("<p>Test</p>")
        .text("Test")
        .build()
    )
    result = ms.emails.send(msg)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
