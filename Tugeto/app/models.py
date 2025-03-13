from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """
    Kullanıcı modeli. Django'nun AbstractUser modelini genişletir.
    """
    USER_TYPE_CHOICES = (
        ('student', 'Öğrenci'),
        ('developer', 'Geliştirici'),
        ('instructor', 'Eğitmen'),
        ('company', 'Şirket'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='developer')
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    skills = models.ManyToManyField('Skill', blank=True)
    
    def __str__(self):
        return self.username

class Skill(models.Model):
    """
    Kullanıcıların sahip olabileceği yetenekler.
    """
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('P', 'Programcı'),
        ('M', 'Mühendis'),
        ('D', 'Diğer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES, default='P')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class ForumCategory(models.Model):
    """
    Forum kategorileri.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="fas fa-folder", help_text="Font Awesome icon class")
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Forum Categories"
        ordering = ['order', 'name']
    
    def get_topic_count(self):
        return self.topics.count()
    
    def get_post_count(self):
        count = 0
        for topic in self.topics.all():
            count += topic.comments.count() + 1  # +1 for the topic itself
        return count

class ForumTopic(models.Model):
    """
    Forum konuları.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_comment_count(self):
        return self.comments.count()
    
    def get_last_comment(self):
        return self.comments.order_by('-created_at').first()

class ForumComment(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_solution = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.topic.title}"

class CompetitionCategory(models.Model):
    """
    Yarışma kategorileri.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True)  # Font Awesome icon class
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Yarışma Kategorileri"

class Competition(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Geliştirme'),
        ('ai', 'Yapay Zeka'),
        ('game', 'Oyun Geliştirme'),
        ('mobile', 'Mobil Uygulama'),
        ('other', 'Diğer'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Başlangıç'),
        ('intermediate', 'Orta'),
        ('advanced', 'İleri'),
        ('all', 'Tüm Seviyeler'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Yakında'),
        ('active', 'Aktif'),
        ('completed', 'Tamamlandı'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    prize = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='competition_images/')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    
    max_participants = models.PositiveIntegerField()
    current_participants = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_competitions')
    participants = models.ManyToManyField(User, through='CompetitionParticipant', related_name='participated_competitions')
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_completion_percentage(self):
        if self.max_participants > 0:
            return (self.current_participants / self.max_participants) * 100
        return 0
    
    def get_remaining_time(self):
        if self.status == 'upcoming':
            return self.start_date - timezone.now()
        elif self.status == 'active':
            return self.end_date - timezone.now()
        return None

class CompetitionParticipant(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    submission = models.FileField(upload_to='competition_submissions/', null=True, blank=True)
    submission_date = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    
    class Meta:
        unique_together = ['competition', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.competition.title}"

class CompetitionAnnouncement(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.competition.title} - {self.title}"

class BlogPost(models.Model):
    """
    Blog yazıları.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Tag(models.Model):
    """
    Blog yazıları için etiketler.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Notification(models.Model):
    """
    Kullanıcı bildirimleri.
    """
    NOTIFICATION_TYPES = (
        ('forum_reply', 'Forum Yanıtı'),
        ('forum_mention', 'Forum Bahsetme'),
        ('competition_start', 'Yarışma Başladı'),
        ('competition_end', 'Yarışma Bitti'),
        ('new_follower', 'Yeni Takipçi'),
        ('system', 'Sistem Bildirimi'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    related_link = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']

class Message(models.Model):
    """
    Kullanıcılar arası mesajlaşma.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"
    
    class Meta:
        ordering = ['-created_at']
