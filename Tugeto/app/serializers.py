from rest_framework import serializers
from .models import (
    User, Skill, ForumCategory, ForumTopic, ForumComment,
    CompetitionCategory, Competition, CompetitionParticipant,
    BlogPost, Tag, Notification, Message
)

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 
                 'bio', 'profile_image', 'github_url', 'linkedin_url', 'website_url', 
                 'skills', 'date_joined']
        read_only_fields = ['date_joined']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'user_type']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=validated_data.get('user_type', 'developer')
        )
        return user

class ForumCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumCategory
        fields = '__all__'

class ForumTopicListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = ForumCategorySerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumTopic
        fields = ['id', 'title', 'author', 'category', 'created_at', 'updated_at', 
                 'views', 'is_pinned', 'is_closed', 'slug', 'comment_count']
    
    def get_comment_count(self, obj):
        return obj.comments.count()

class ForumCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = ForumComment
        fields = ['id', 'topic', 'author', 'content', 'created_at', 'updated_at', 
                 'parent', 'is_solution']
        read_only_fields = ['created_at', 'updated_at', 'is_solution']

class ForumTopicDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = ForumCategorySerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumTopic
        fields = ['id', 'title', 'content', 'author', 'category', 'created_at', 
                 'updated_at', 'views', 'is_pinned', 'is_closed', 'slug', 'comments']
    
    def get_comments(self, obj):
        # Sadece üst seviye yorumları getir
        comments = obj.comments.filter(parent=None)
        return ForumCommentSerializer(comments, many=True).data

class CompetitionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionCategory
        fields = '__all__'

class CompetitionListSerializer(serializers.ModelSerializer):
    category = CompetitionCategorySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Competition
        fields = ['id', 'title', 'category', 'level', 'status', 'start_date', 
                 'end_date', 'prize', 'created_by', 'participant_count', 'slug']

class CompetitionParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CompetitionParticipant
        fields = ['id', 'competition', 'user', 'joined_at', 'submission_url', 
                 'submission_date', 'score']
        read_only_fields = ['joined_at', 'score']

class CompetitionDetailSerializer(serializers.ModelSerializer):
    category = CompetitionCategorySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    participants = serializers.SerializerMethodField()
    
    class Meta:
        model = Competition
        fields = ['id', 'title', 'description', 'category', 'level', 'status', 
                 'start_date', 'end_date', 'prize', 'rules', 'created_by', 
                 'participants', 'max_participants', 'slug']
    
    def get_participants(self, obj):
        participants = CompetitionParticipant.objects.filter(competition=obj)
        return CompetitionParticipantSerializer(participants, many=True).data

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class BlogPostListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'author', 'created_at', 'published_at', 
                 'is_published', 'featured_image', 'tags', 'slug', 'views']

class BlogPostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 
                 'published_at', 'is_published', 'featured_image', 'tags', 'slug', 'views']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'notification_type', 'title', 'message', 
                 'created_at', 'is_read', 'related_link']
        read_only_fields = ['created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'created_at', 'is_read']
        read_only_fields = ['created_at'] 