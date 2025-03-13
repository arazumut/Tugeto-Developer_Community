#Author : K. Umut Araz
#Date : 13.03.2025 3.10am

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    User, Skill, ForumCategory, ForumTopic, ForumComment,
    CompetitionCategory, Competition, CompetitionParticipant,
    BlogPost, Tag, Notification, Message
)
from .serializers import (
    UserSerializer, UserCreateSerializer, SkillSerializer,
    ForumCategorySerializer, ForumTopicListSerializer, ForumTopicDetailSerializer,
    ForumCommentSerializer, CompetitionCategorySerializer, CompetitionListSerializer,
    CompetitionDetailSerializer, CompetitionParticipantSerializer,
    BlogPostListSerializer, BlogPostDetailSerializer, TagSerializer,
    NotificationSerializer, MessageSerializer
)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Nesnenin sahibi ise düzenleme izni verir, değilse sadece okuma izni verir.
    """
    def has_object_permission(self, request, view, obj):
        # Okuma izinleri GET, HEAD veya OPTIONS istekleri için verilir
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Yazma izinleri sadece nesnenin sahibine verilir
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'sender'):
            return obj.sender == request.user
        return obj == request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class ForumCategoryViewSet(viewsets.ModelViewSet):
    queryset = ForumCategory.objects.all()
    serializer_class = ForumCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class ForumTopicViewSet(viewsets.ModelViewSet):
    queryset = ForumTopic.objects.all().select_related('author', 'category').annotate(comment_count=Count('comments'))
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_pinned', 'is_closed']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views', 'comment_count']
    ordering = ['-is_pinned', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ForumTopicDetailSerializer
        return ForumTopicListSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Görüntülenme sayısını artır
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        topic = self.get_object()
        serializer = ForumCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, topic=topic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForumCommentViewSet(viewsets.ModelViewSet):
    queryset = ForumComment.objects.all()
    serializer_class = ForumCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_solution(self, request, pk=None):
        comment = self.get_object()
        topic = comment.topic
        
        # Sadece konu sahibi çözüm olarak işaretleyebilir
        if request.user != topic.author:
            return Response({"detail": "Bu işlemi yapmaya yetkiniz yok."}, status=status.HTTP_403_FORBIDDEN)
        
        # Diğer çözümleri kaldır
        topic.comments.filter(is_solution=True).update(is_solution=False)
        
        # Bu yorumu çözüm olarak işaretle
        comment.is_solution = True
        comment.save()
        
        return Response({"detail": "Yorum çözüm olarak işaretlendi."})

class CompetitionCategoryViewSet(viewsets.ModelViewSet):
    queryset = CompetitionCategory.objects.all()
    serializer_class = CompetitionCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all().select_related('category', 'created_by').annotate(participant_count=Count('participants'))
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'participant_count']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CompetitionDetailSerializer
        return CompetitionListSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        competition = self.get_object()
        
        # Kullanıcı zaten katılmış mı kontrol et
        if CompetitionParticipant.objects.filter(competition=competition, user=request.user).exists():
            return Response({"detail": "Bu yarışmaya zaten katıldınız."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Yarışma aktif mi kontrol et
        if competition.status != 'active':
            return Response({"detail": "Bu yarışma şu anda aktif değil."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Maksimum katılımcı sayısı kontrol et
        if competition.participants.count() >= competition.max_participants:
            return Response({"detail": "Bu yarışma maksimum katılımcı sayısına ulaştı."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Yarışmaya katıl
        participant = CompetitionParticipant.objects.create(competition=competition, user=request.user)
        serializer = CompetitionParticipantSerializer(participant)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        competition = self.get_object()
        
        # Kullanıcı yarışmaya katılmış mı kontrol et
        try:
            participant = CompetitionParticipant.objects.get(competition=competition, user=request.user)
        except CompetitionParticipant.DoesNotExist:
            return Response({"detail": "Bu yarışmaya katılmadınız."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Yarışma aktif mi kontrol et
        if not competition.is_active:
            return Response({"detail": "Bu yarışma şu anda aktif değil."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Submission URL'i güncelle
        submission_url = request.data.get('submission_url')
        if not submission_url:
            return Response({"detail": "Gönderim URL'i gereklidir."}, status=status.HTTP_400_BAD_REQUEST)
        
        participant.submission_url = submission_url
        participant.submission_date = timezone.now()
        participant.save()
        
        serializer = CompetitionParticipantSerializer(participant)
        return Response(serializer.data)

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all().select_related('author')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'tags']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'published_at', 'views']
    ordering = ['-published_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Yayınlanmamış gönderileri sadece yazarları görebilir
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True)
        elif not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True) | queryset.filter(author=self.request.user)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Görüntülenme sayısını artır
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"detail": "Bildirim okundu olarak işaretlendi."})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({"detail": "Tüm bildirimler okundu olarak işaretlendi."})

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        if message.receiver != request.user:
            return Response({"detail": "Bu işlemi yapmaya yetkiniz yok."}, status=status.HTTP_403_FORBIDDEN)
        
        message.is_read = True
        message.save()
        return Response({"detail": "Mesaj okundu olarak işaretlendi."})
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Kullanıcının tüm konuşmalarını listeler"""
        user = request.user
        
        # Kullanıcının mesajlaştığı diğer kullanıcıları bul
        sent_to = Message.objects.filter(sender=user).values_list('receiver', flat=True).distinct()
        received_from = Message.objects.filter(receiver=user).values_list('sender', flat=True).distinct()
        
        # Tekrarlanan kullanıcıları kaldır
        user_ids = set(list(sent_to) + list(received_from))
        users = User.objects.filter(id__in=user_ids)
        
        # Her kullanıcı için son mesajı bul
        conversations = []
        for other_user in users:
            last_message = Message.objects.filter(
                (Q(sender=user) & Q(receiver=other_user)) |
                (Q(sender=other_user) & Q(receiver=user))
            ).order_by('-created_at').first()
            
            if last_message:
                conversations.append({
                    'user': UserSerializer(other_user).data,
                    'last_message': MessageSerializer(last_message).data,
                    'unread_count': Message.objects.filter(sender=other_user, receiver=user, is_read=False).count()
                })
        
        return Response(conversations) 