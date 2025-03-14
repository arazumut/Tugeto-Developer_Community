from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_simple_email(subject, message, recipient_list):
    """
    Basit bir metin e-postası gönderir.
    """
    try:
        return send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception as e:
        print(f"E-posta gönderme hatası: {e}")
        return False

def send_html_email(subject, template_name, context, recipient_list):
    """
    HTML formatında şablona dayalı bir e-posta gönderir.
    """
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        
        email.attach_alternative(html_content, "text/html")
        return email.send()
    except Exception as e:
        print(f"HTML e-posta gönderme hatası: {e}")
        return False 