"""
Email utilities for the users app.

Usage:
    from apps.users.emails import send_otp_email
    send_otp_email(user, otp_code)
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_otp_email(email: str, code: str, expiry_minutes: int = 10) -> None:
    """Send an OTP code to the given email address."""
    context = {
        "code": code,
        "expiry_minutes": expiry_minutes,
        "support_email": settings.DEFAULT_FROM_EMAIL,
    }

    subject = "Votre code de vérification"
    from_email = settings.DEFAULT_FROM_EMAIL
    text_body = (
        f"Votre code de vérification est : {code}\n"
        f"Il expire dans {expiry_minutes} minutes.\n\n"
        "Si vous n'avez pas demandé ce code, ignorez cet email."
    )
    html_body = render_to_string("emails/otp_code.html", context)

    msg = EmailMultiAlternatives(subject, text_body, from_email, [email])
    msg.attach_alternative(html_body, "text/html")
    msg.send()
