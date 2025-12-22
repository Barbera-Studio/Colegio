import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings


def send_announcement_email(to_email, subject, html_content):
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        print("Error al enviar correo:", e)
        return None
