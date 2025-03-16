"""
Bu dosyayı Django shell'de çalıştırmak için:
python manage.py shell < test_email.py

Bu komutlar Django shell'de manuel olarak da çalıştırılabilir.
"""

# E-posta gönderme fonksiyonunu import et
from django.core.mail import send_mail
from django.conf import settings

# Test e-postası gönder
print("Test e-postası gönderiliyor...")
result = send_mail(
    subject='Django Test E-postası',
    message='Bu bir test e-postasıdır.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['testuser@example.com'],
    fail_silently=False,
)

print(f"E-posta gönderildi: {result}")

# Çıkış
print("Test tamamlandı!") 