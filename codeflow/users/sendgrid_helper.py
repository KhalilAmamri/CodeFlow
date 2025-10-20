import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def sendgrid_send_email(to_email, subject, body):
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('SENDGRID_FROM_EMAIL')
    if not api_key or not from_email:
        raise RuntimeError('SendGrid API key or sender email not set')
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False
