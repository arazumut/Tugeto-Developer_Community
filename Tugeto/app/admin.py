#Author : K. Umut Araz
#Date : 13.03.2025 ö3.08am

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Skill, ForumCategory, ForumTopic, ForumComment,
    CompetitionCategory, Competition, CompetitionParticipant,
    BlogPost, Tag, Notification, Message, CompetitionAnnouncement
)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Bilgiler', {'fields': ('user_type', 'bio', 'profile_image', 'github_url', 'linkedin_url', 'website_url', 'skills')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Ek Bilgiler', {'fields': ('user_type', 'bio', 'profile_image', 'github_url', 'linkedin_url', 'website_url', 'skills')}),
    )
    filter_horizontal = ('groups', 'user_permissions', 'skills')

class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'views', 'is_pinned', 'is_closed')
    list_filter = ('category', 'is_pinned', 'is_closed', 'created_at')
    search_fields = ('title', 'content', 'author__username')

class ForumCommentAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'created_at', 'is_solution')
    list_filter = ('is_solution', 'created_at')
    search_fields = ('content', 'author__username', 'topic__title')

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'level', 'status', 'start_date', 'end_date', 'organizer']
    list_filter = ['category', 'level', 'status']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'

class CompetitionParticipantAdmin(admin.ModelAdmin):
    list_display = ('competition', 'user', 'joined_at', 'submission_date', 'score')
    list_filter = ('competition', 'joined_at', 'submission_date')
    search_fields = ('competition__title', 'user__username')

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_published', 'views')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'content')

# Modelleri admin paneline kaydet
admin.site.register(User, CustomUserAdmin)
admin.site.register(Skill)
admin.site.register(ForumCategory)
admin.site.register(ForumTopic, ForumTopicAdmin)
admin.site.register(ForumComment, ForumCommentAdmin)
admin.site.register(CompetitionCategory)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(CompetitionParticipant, CompetitionParticipantAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Tag)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(CompetitionAnnouncement)
