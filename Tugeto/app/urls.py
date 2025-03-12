from django.urls import path
from . import views
from . import auth_views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('forum/', views.forum, name='forum'),
    path('yarisma/', views.yarisma, name='yarisma'),
    path('hakkimizda/', views.hakkimizda, name='hakkimizda'),
    path('iletisim/', views.iletisim, name='iletisim'),
    
    # Kimlik doğrulama URL'leri
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
] 