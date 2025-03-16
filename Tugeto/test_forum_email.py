#!/usr/bin/env python
"""
Forum konusu oluşturarak e-posta bildirimini test etmek için script.
"""
import os
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tugeto.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from app.models import ForumCategory, ForumTopic, EmailPreference
from app.views import send_forum_topic_notification
from django.urls import reverse

User = get_user_model()

def setup_test_data():
    """Test için gerekli verileri oluşturur."""
    print("Test verileri oluşturuluyor...")
    
    # Test kullanıcıları oluştur
    user1, created = User.objects.get_or_create(
        username='testuser1',
        defaults={
            'email': 'testuser1@example.com',
            'is_active': True
        }
    )
    if created:
        user1.set_password('testpassword123')
        user1.save()
        print(f"Kullanıcı oluşturuldu: {user1.username}")
    else:
        print(f"Kullanıcı zaten var: {user1.username}")
    
    user2, created = User.objects.get_or_create(
        username='testuser2',
        defaults={
            'email': 'testuser2@example.com',
            'is_active': True
        }
    )
    if created:
        user2.set_password('testpassword123')
        user2.save()
        print(f"Kullanıcı oluşturuldu: {user2.username}")
    else:
        print(f"Kullanıcı zaten var: {user2.username}")
    
    # E-posta tercihleri oluştur
    pref1, created = EmailPreference.objects.get_or_create(
        user=user1,
        defaults={'new_forum_topics': True}
    )
    if created:
        print(f"E-posta tercihi oluşturuldu: {user1.username}")
    else:
        pref1.new_forum_topics = True
        pref1.save()
        print(f"E-posta tercihi güncellendi: {user1.username}")
    
    pref2, created = EmailPreference.objects.get_or_create(
        user=user2,
        defaults={'new_forum_topics': True}
    )
    if created:
        print(f"E-posta tercihi oluşturuldu: {user2.username}")
    else:
        pref2.new_forum_topics = True
        pref2.save()
        print(f"E-posta tercihi güncellendi: {user2.username}")
    
    # Forum kategorisi oluştur
    category, created = ForumCategory.objects.get_or_create(
        name='Test Kategorisi',
        defaults={
            'description': 'Test kategori açıklaması',
            'slug': 'test-kategorisi'
        }
    )
    if created:
        print(f"Kategori oluşturuldu: {category.name}")
    else:
        print(f"Kategori zaten var: {category.name}")
    
    return user1, user2, category

def create_forum_topic(author, category):
    """Yeni bir forum konusu oluşturur ve e-posta bildirimini test eder."""
    print(f"\n{author.username} kullanıcısı ile yeni bir forum konusu oluşturuluyor...")
    
    # Yeni bir forum konusu oluştur
    topic = ForumTopic.objects.create(
        title='Test Konu Başlığı',
        content='Bu bir test forum konusudur. E-posta bildirimini test etmek için oluşturulmuştur.',
        category=category,
        author=author
    )
    print(f"Forum konusu oluşturuldu: {topic.title}")
    
    # RequestFactory ile sahte bir istek oluştur
    factory = RequestFactory()
    request = factory.get('/')
    
    # Mutlak URL oluşturmak için host bilgisi ekle
    request.META['HTTP_HOST'] = '127.0.0.1:8000'
    request.scheme = 'http'
    
    # send_forum_topic_notification fonksiyonunu çağır
    print("E-posta bildirimi gönderiliyor...")
    send_forum_topic_notification(request, topic)
    print("E-posta bildirimi gönderildi. Konsol çıktısını kontrol edin.")
    
    return topic

if __name__ == '__main__':
    # Test verilerini oluştur
    user1, user2, category = setup_test_data()
    
    # Forum konusu oluştur ve e-posta bildirimini test et
    topic = create_forum_topic(user1, category)
    
    print("\nTest tamamlandı!")
    print("E-posta bildirimi konsola yazdırıldı (settings.py'de EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' ayarı yapıldıysa).")
    print("Gerçek e-posta göndermek için settings.py dosyasındaki EMAIL_BACKEND ayarını 'django.core.mail.backends.smtp.EmailBackend' olarak değiştirin.") 