#Author : K. Umut Araz
#Date : 13.03.2025 ö3.08am

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'skills', api_views.SkillViewSet)
router.register(r'forum/categories', api_views.ForumCategoryViewSet)
router.register(r'forum/topics', api_views.ForumTopicViewSet)
router.register(r'forum/comments', api_views.ForumCommentViewSet)
router.register(r'competitions/categories', api_views.CompetitionCategoryViewSet)
router.register(r'competitions', api_views.CompetitionViewSet)
router.register(r'blog/posts', api_views.BlogPostViewSet)
router.register(r'blog/tags', api_views.TagViewSet)
router.register(r'notifications', api_views.NotificationViewSet, basename='notification')
router.register(r'messages', api_views.MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
] 