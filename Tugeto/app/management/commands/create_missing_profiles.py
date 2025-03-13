from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from app.models import User, Profile

class Command(BaseCommand):
    help = 'Profili olmayan kullanıcılar için profil oluşturur'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            try:
                # Profil var mı kontrol et
                profile = user.profile
                self.stdout.write(f"Kullanıcı {user.username} için profil zaten mevcut.")
            except ObjectDoesNotExist:
                # Profil yoksa oluştur
                Profile.objects.create(user=user)
                created_count += 1
                self.stdout.write(f"Kullanıcı {user.username} için yeni profil oluşturuldu.")
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'{created_count} kullanıcı için yeni profil oluşturuldu.'))
        else:
            self.stdout.write(self.style.SUCCESS('Tüm kullanıcıların profili zaten mevcut.')) 