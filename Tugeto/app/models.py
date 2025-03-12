from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

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

class ForumCategory(models.Model):
    """
    Forum kategorileri.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True)  # Font Awesome icon class
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Forum Kategorileri"

class ForumTopic(models.Model):
    """
    Forum konuları.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class ForumComment(MPTTModel):
    """
    Forum yorumları. MPTT modeli kullanarak ağaç yapısı oluşturur.
    """
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_solution = models.BooleanField(default=False)
    
    class MPTTMeta:
        order_insertion_by = ['created_at']
    
    def __str__(self):
        return f"Yorum: {self.content[:50]}..."

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
    """
    Yarışma modeli.
    """
    LEVEL_CHOICES = (
        ('beginner', 'Başlangıç'),
        ('intermediate', 'Orta'),
        ('advanced', 'İleri'),
    )
    
    STATUS_CHOICES = (
        ('upcoming', 'Yakında'),
        ('active', 'Aktif'),
        ('completed', 'Tamamlandı'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(CompetitionCategory, on_delete=models.CASCADE, related_name='competitions')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    prize = models.CharField(max_length=200)
    rules = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_competitions')
    participants = models.ManyToManyField(User, through='CompetitionParticipant', related_name='participating_competitions')
    max_participants = models.PositiveIntegerField(default=100)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.status == 'active'
    
    @property
    def participant_count(self):
        return self.participants.count()
    
    def __str__(self):
        return self.title

class CompetitionParticipant(models.Model):
    """
    Yarışma katılımcıları.
    """
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    submission_url = models.URLField(blank=True, null=True)
    submission_date = models.DateTimeField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    
    class Meta:
        unique_together = ('competition', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.competition.title}"

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
