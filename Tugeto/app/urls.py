from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('forum/', views.forum, name='forum'),
    path('yarisma/', views.yarisma, name='yarisma'),
    path('hakkimizda/', views.hakkimizda, name='hakkimizda'),
    path('iletisim/', views.iletisim, name='iletisim'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
] 