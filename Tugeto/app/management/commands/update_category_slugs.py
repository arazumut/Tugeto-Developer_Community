from django.core.management.base import BaseCommand
from app.models import ForumCategory
from django.utils.text import slugify
from unidecode import unidecode

class Command(BaseCommand):
    help = 'Kategori slug\'larını günceller'

    def handle(self, *args, **kwargs):
        categories = ForumCategory.objects.all()
        for category in categories:
            old_slug = category.slug
            # Türkçe karakterleri ve boşlukları düzelt
            new_slug = slugify(unidecode(category.name.lower()))
            category.slug = new_slug
            category.save()
            self.stdout.write(f'Kategori güncellendi: {old_slug} -> {new_slug}')
        
        self.stdout.write(self.style.SUCCESS('Tüm kategori slug\'ları güncellendi!')) 