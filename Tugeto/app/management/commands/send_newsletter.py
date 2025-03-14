from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.utils import send_html_email
from django.utils import timezone
import argparse

class Command(BaseCommand):
    help = 'Bülten abonelerine toplu e-posta gönderir'

    def add_arguments(self, parser):
        parser.add_argument('--subject', type=str, required=True, help='E-posta konusu')
        parser.add_argument('--template', type=str, required=True, help='E-posta şablonu (app/emails/ klasöründeki)')
        parser.add_argument('--test', action='store_true', help='Test modu (sadece bir e-posta gönderir)')
        parser.add_argument('--test-email', type=str, help='Test için e-posta adresi')

    def handle(self, *args, **options):
        subject = options['subject']
        template_name = f"app/emails/{options['template']}"
        test_mode = options['test']
        test_email = options['test_email']
        
        # Şablon var mı kontrol et
        try:
            from django.template.loader import get_template
            get_template(template_name)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Şablon bulunamadı: {e}'))
            return
        
        # Test modu
        if test_mode:
            if not test_email:
                self.stdout.write(self.style.ERROR('Test modu için --test-email parametresi gereklidir.'))
                return
                
            self.stdout.write(self.style.WARNING(f'TEST MODU: {test_email} adresine e-posta gönderiliyor...'))
            
            try:
                send_html_email(
                    subject=subject,
                    template_name=template_name,
                    context={
                        'date': timezone.now(),
                        'unsubscribe_url': '#',
                    },
                    recipient_list=[test_email]
                )
                self.stdout.write(self.style.SUCCESS(f'Test e-postası başarıyla gönderildi: {test_email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Test e-postası gönderilirken hata oluştu: {e}'))
            
            return
        
        # Bülten almak isteyen kullanıcıları bul
        subscribers = User.objects.filter(
            email_preferences__newsletter=True,
            is_active=True
        ).exclude(email='')
        
        total = subscribers.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('Bülten almak isteyen aktif kullanıcı bulunamadı.'))
            return
        
        self.stdout.write(self.style.WARNING(f'Toplam {total} kullanıcıya e-posta gönderilecek. Devam etmek istiyor musunuz? (evet/hayır)'))
        confirm = input().lower()
        
        if confirm != 'evet':
            self.stdout.write(self.style.WARNING('İşlem iptal edildi.'))
            return
        
        # E-postaları gönder
        success_count = 0
        error_count = 0
        
        for subscriber in subscribers:
            try:
                # Abonelikten çıkma URL'si
                unsubscribe_url = f"/profile/email-preferences/"
                
                send_html_email(
                    subject=subject,
                    template_name=template_name,
                    context={
                        'user': subscriber,
                        'email': subscriber.email,
                        'date': timezone.now(),
                        'unsubscribe_url': unsubscribe_url,
                    },
                    recipient_list=[subscriber.email]
                )
                success_count += 1
                self.stdout.write(f'E-posta gönderildi: {subscriber.email}')
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'Hata: {subscriber.email} - {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Toplu e-posta gönderimi tamamlandı. Başarılı: {success_count}, Hata: {error_count}')) 