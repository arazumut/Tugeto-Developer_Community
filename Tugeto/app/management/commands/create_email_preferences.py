from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import EmailPreference

class Command(BaseCommand):
    help = 'Mevcut kullanıcılar için e-posta tercihlerini oluşturur'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            _, created = EmailPreference.objects.get_or_create(user=user)
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} kullanıcı için e-posta tercihleri oluşturuldu.')) 