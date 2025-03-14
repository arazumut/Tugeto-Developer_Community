from django.core.management.base import BaseCommand
from app.models import ForumCategory
from django.utils.text import slugify
from unidecode import unidecode

class Command(BaseCommand):
    help = 'Forum kategorilerini oluşturur'

    def handle(self, *args, **kwargs):
        # Önce mevcut kategorileri temizle
        ForumCategory.objects.all().delete()

        # Ana kategoriler
        categories = {
            'Yazılım': [
                'Genel Yazılım',
                'Web Geliştirme',
                'Mobil Uygulama',
                'Veri Bilimi'
            ],
            'Tıp': [
                'Genel Tıp',
                'Klinik Araştırmalar',
                'Tıbbi Teknolojiler'
            ],
            'Teknoloji': [
                'Yapay Zeka',
                'Robotik',
                'Blockchain',
                'IoT'
            ],
            'Diğer': [
                'Genel Konular',
                'Duyurular',
                'Yardım'
            ]
        }

        for main_category, sub_categories in categories.items():
            # Ana kategoriyi oluştur
            parent = ForumCategory.objects.create(
                name=main_category,
                slug=slugify(unidecode(main_category.lower())),
                description=f'{main_category} ile ilgili konular',
                icon='fas fa-folder'
            )
            
            # Alt kategorileri oluştur
            for sub_category in sub_categories:
                ForumCategory.objects.create(
                    name=sub_category,
                    slug=slugify(unidecode(sub_category.lower())),
                    description=f'{sub_category} ile ilgili konular',
                    parent=parent,
                    icon='fas fa-folder'
                )

        self.stdout.write(self.style.SUCCESS('Forum kategorileri başarıyla oluşturuldu!')) 