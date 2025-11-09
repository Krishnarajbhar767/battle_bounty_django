from django.core.mail import send_mail as django_send_mail
from django.conf import settings 
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from utils.constaint import COMPANY_NAME
import threading
def send_mail(subject , recipient_list, context=None, template_name=None):
    from_email = settings.EMAIL_HOST_USER or 'noreply@yourdomain.com'
    
    html_message = None
    plain_message = ""

    if template_name:
        try:
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
        except Exception as e:
            print(f"Error rendering email template {template_name}: {e}")
            plain_message = subject
    elif context and 'message_body' in context:
        plain_message = context.get('message_body', 'An important update from us.')
    else:
        plain_message = "This is a default email message."

    # --- THREAD MAGIC STARTS HERE ---
    def _send():
        try:
            django_send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
                html_message=html_message
            )
        except Exception as e:
            print(f"Error sending email to {recipient_list}: {e}")

    threading.Thread(target=_send).start()
    return True

# -----------------------------------------------------------
# SPECIFIC OTP SENDER
# -----------------------------------------------------------

def send_otp_email(recipient_email, otp_code, user_first_name=None):
    context = {
        'otp_code': otp_code,
        'user_first_name': user_first_name or "User",
        'expiration_minutes': 5,
        'message_body': f"""
        Hello {user_first_name or "User"},

        Your One-Time Password (OTP) for verification is: {otp_code}

        This code will expire in 5 minutes.

        If you did not request this, please ignore this email.

        Best Regards,
        The Support Team 
        """
    }

    return send_mail(
        subject=f'Your Account Verification Code (OTP) - {COMPANY_NAME}',
        recipient_list=[recipient_email],
        context=context,
        template_name=None
    )
