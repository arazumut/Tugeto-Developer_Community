#Author : K. Umut Araz
#Date : 13.03.2025 3.15am

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.conf import settings
from app.models import ForumCategory, ForumTopic, EmailPreference
from app.views import create_topic, send_forum_topic_notification

User = get_user_model()

class ForumEmailNotificationTest(TestCase):
    def setUp(self):
        
        self.factory = RequestFactory()
        
        self.user1 = User.objects.create_user(
            username='testuser1', 
            email='testuser1@example.com', 
            password='testpassword123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='testuser2@example.com', 
            password='testpassword123'
        )
        self.user3 = User.objects.create_user(
            username='testuser3', 
            email='testuser3@example.com', 
            password='testpassword123'
        )
        
        EmailPreference.objects.create(user=self.user1, new_forum_topics=True)
        EmailPreference.objects.create(user=self.user2, new_forum_topics=False)  
        EmailPreference.objects.create(user=self.user3, new_forum_topics=True)
        
        self.category = ForumCategory.objects.create(
            name='Test Kategorisi',
            description='Test kategori açıklaması',
            slug='test-kategorisi'
        )
    
    def test_forum_topic_notification(self):
        """Yeni forum konusu oluşturulduğunda doğru kullanıcılara e-posta gönderildiğini test eder"""
        mail.outbox = []
        
        self.client.login(username='testuser1', password='testpassword123')
        
        response = self.client.post(
            reverse('app:create_topic'),
            {
                'title': 'Test Konu Başlığı',
                'content': 'Test konu içeriği',
                'category': self.category.id
            }
        )
        
        self.assertEqual(response.status_code, 302)
        
        self.assertTrue(ForumTopic.objects.filter(title='Test Konu Başlığı').exists())
        
        # E-posta gönderildi mi kontrol et
        self.assertEqual(len(mail.outbox), 1)  # Sadece 1 e-posta gönderilmeli (user3'e)
        
        # E-postanın doğru kişiye gönderildiğini kontrol et
        self.assertEqual(mail.outbox[0].to, [self.user3.email])
        
        # E-posta konusunun doğru olduğunu kontrol et
        self.assertEqual(mail.outbox[0].subject, 'Yeni Forum Konusu: Test Konu Başlığı')
    
    def test_send_forum_topic_notification_directly(self):
        """send_forum_topic_notification fonksiyonunu doğrudan test eder"""
        # Mail kutusunu temizle
        mail.outbox = []
        
        # Yeni bir forum konusu oluştur
        topic = ForumTopic.objects.create(
            title='Doğrudan Test Konusu',
            content='Doğrudan test içeriği',
            category=self.category,
            author=self.user1
        )
        
        # RequestFactory ile sahte bir istek oluştur
        request = self.factory.get('/')
        
        # send_forum_topic_notification fonksiyonunu çağır
        send_forum_topic_notification(request, topic)
        
        # E-posta gönderildi mi kontrol et
        self.assertEqual(len(mail.outbox), 1)
        
        # E-postanın doğru kişiye gönderildiğini kontrol et
        self.assertEqual(mail.outbox[0].to, [self.user3.email])
        
        # E-posta konusunun doğru olduğunu kontrol et
        self.assertEqual(mail.outbox[0].subject, 'Yeni Forum Konusu: Doğrudan Test Konusu')
