#Author : K. Umut Araz
#Date : 13.03.2025 3.16am

from django.urls import path
from . import views
from . import auth_views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('forum/', views.forum, name='forum'),
    path('forum/category/<slug:slug>/', views.forum_category, name='forum_category'),
    path('forum/topic/<int:topic_id>/', views.forum_topic, name='forum_topic'),
    path('forum/create/', views.create_topic, name='create_topic'),
    path('forum/create/<slug:category_slug>/', views.create_topic, name='create_topic_category'),
    path('forum/edit/<int:topic_id>/', views.edit_topic, name='edit_topic'),
    path('forum/delete/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('forum/comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('forum/comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('forum/comment/solution/<int:comment_id>/', views.mark_solution, name='mark_solution'),
    path('forum/search/', views.search_forum, name='search_forum'),
    path('yarisma/', views.yarisma, name='yarisma'),
    path('yarisma/olustur/', views.create_competition, name='create_competition'),
    path('yarisma/<slug:slug>/', views.competition_detail, name='competition_detail'),
    path('hakkimizda/', views.hakkimizda, name='hakkimizda'),
    path('iletisim/', views.iletisim, name='iletisim'),
    
    # Kimlik doğrulama URL'leri
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),

    path('yarisma/yonetim/', views.manage_competitions, name='manage_competitions'),
    path('yarisma/duzenle/<slug:slug>/', views.edit_competition, name='edit_competition'),
    path('yarisma/sil/<slug:slug>/', views.delete_competition, name='delete_competition'),
] 