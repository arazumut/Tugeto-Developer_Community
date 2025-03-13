from django.core.management.base import BaseCommand
from app.models import ForumCategory
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Forum kategorilerini oluşturur'

    def handle(self, *args, **options):
        # Ana kategoriler
        categories = [
            {
                'name': 'Yazılım',
                'description': 'Programlama dilleri, yazılım geliştirme, algoritmalar ve kodlama ile ilgili konular',
                'icon': 'fas fa-code',
                'order': 1
            },
            {
                'name': 'Tıp',
                'description': 'Sağlık, tıbbi araştırmalar, hastalıklar ve tedaviler hakkında tartışmalar',
                'icon': 'fas fa-heartbeat',
                'order': 2
            },
            {
                'name': 'Teknoloji',
                'description': 'Yeni teknolojiler, donanım, yapay zeka, robotik ve teknolojik gelişmeler',
                'icon': 'fas fa-microchip',
                'order': 3
            },
            {
                'name': 'Diğer',
                'description': 'Diğer kategorilere uymayan genel konular',
                'icon': 'fas fa-folder',
                'order': 4
            }
        ]
        
        # Alt kategoriler
        subcategories = {
            'Yazılım': [
                {
                    'name': 'Web Geliştirme',
                    'description': 'HTML, CSS, JavaScript, frontend ve backend web geliştirme',
                    'icon': 'fas fa-globe',
                    'order': 1
                },
                {
                    'name': 'Mobil Uygulama',
                    'description': 'Android, iOS ve cross-platform mobil uygulama geliştirme',
                    'icon': 'fas fa-mobile-alt',
                    'order': 2
                },
                {
                    'name': 'Veri Bilimi',
                    'description': 'Veri analizi, makine öğrenmesi ve büyük veri teknolojileri',
                    'icon': 'fas fa-chart-bar',
                    'order': 3
                }
            ],
            'Tıp': [
                {
                    'name': 'Genel Sağlık',
                    'description': 'Genel sağlık konuları ve tavsiyeler',
                    'icon': 'fas fa-user-md',
                    'order': 1
                },
                {
                    'name': 'Tıbbi Araştırmalar',
                    'description': 'Yeni tıbbi araştırmalar ve bilimsel gelişmeler',
                    'icon': 'fas fa-microscope',
                    'order': 2
                }
            ],
            'Teknoloji': [
                {
                    'name': 'Yapay Zeka',
                    'description': 'Yapay zeka, derin öğrenme ve bilgisayarlı görü',
                    'icon': 'fas fa-robot',
                    'order': 1
                },
                {
                    'name': 'Donanım',
                    'description': 'Bilgisayar donanımı, elektronik ve IoT cihazları',
                    'icon': 'fas fa-laptop',
                    'order': 2
                },
                {
                    'name': 'Oyun Geliştirme',
                    'description': 'Oyun motorları, oyun tasarımı ve oyun programlama',
                    'icon': 'fas fa-gamepad',
                    'order': 3
                }
            ]
        }
        
        created_count = 0
        updated_count = 0
        
        # Ana kategorileri oluştur
        for category_data in categories:
            category, created = ForumCategory.objects.update_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon'],
                    'slug': slugify(category_data['name']),
                    'order': category_data['order']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Kategori oluşturuldu: {category.name}")
            else:
                updated_count += 1
                self.stdout.write(f"Kategori güncellendi: {category.name}")
            
            # Alt kategorileri oluştur
            if category.name in subcategories:
                for subcat_data in subcategories[category.name]:
                    subcategory, sub_created = ForumCategory.objects.update_or_create(
                        name=subcat_data['name'],
                        defaults={
                            'description': subcat_data['description'],
                            'icon': subcat_data['icon'],
                            'slug': slugify(subcat_data['name']),
                            'parent': category,
                            'order': subcat_data['order']
                        }
                    )
                    
                    if sub_created:
                        created_count += 1
                        self.stdout.write(f"Alt kategori oluşturuldu: {subcategory.name} (Ana kategori: {category.name})")
                    else:
                        updated_count += 1
                        self.stdout.write(f"Alt kategori güncellendi: {subcategory.name} (Ana kategori: {category.name})")
        
        if created_count > 0 or updated_count > 0:
            self.stdout.write(self.style.SUCCESS(f'{created_count} yeni kategori oluşturuldu, {updated_count} kategori güncellendi.'))
        else:
            self.stdout.write(self.style.SUCCESS('Hiçbir değişiklik yapılmadı.')) 