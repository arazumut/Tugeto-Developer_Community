#Author : K. Umut Araz
#Date : 13.03.2025 3.13am

#kullanıcı kayıt
#kullanıcı giriş
#kullanıcı profil
#kullanıcı yetenekleri
#kullanıcı yetenekleri ekleme

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, Skill

class UserRegisterForm(UserCreationForm):
    """
    Kullanıcı kayıt formu.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Ad')
    last_name = forms.CharField(max_length=30, required=True, label='Soyad')
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, label='Kullanıcı Tipi')
    skills = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Python, JavaScript, Django, React...'}),
        label='Yetenekler (virgülle ayırın)'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'user_type']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Form alanlarını özelleştir
        self.fields['username'].label = 'Kullanıcı Adı'
        self.fields['email'].label = 'E-posta Adresi'
        self.fields['password1'].label = 'Şifre'
        self.fields['password2'].label = 'Şifre Onayı'
        
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class UserLoginForm(forms.Form):
    """
    Kullanıcı giriş formu.
    """
    username = forms.CharField(max_length=150, label='Kullanıcı Adı')
    password = forms.CharField(widget=forms.PasswordInput, label='Şifre')
    remember_me = forms.BooleanField(required=False, label='Beni Hatırla')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap sınıflarını ekle
        for field_name, field in self.fields.items():
            if field_name != 'remember_me':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'

class UserProfileForm(forms.ModelForm):
    """
    Kullanıcı profil formu.
    """
    skills = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Python, JavaScript, Django, React...'}),
        label='Yetenekler (virgülle ayırın)'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_image', 
                 'github_url', 'linkedin_url', 'website_url', 'user_type']
        labels = {
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'E-posta Adresi',
            'bio': 'Hakkımda',
            'profile_image': 'Profil Resmi',
            'github_url': 'GitHub URL',
            'linkedin_url': 'LinkedIn URL',
            'website_url': 'Web Sitesi URL',
            'user_type': 'Kullanıcı Tipi'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap sınıflarını ekle
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Mevcut yetenekleri virgülle ayrılmış metin olarak göster
        if self.instance and self.instance.pk:
            skills = self.instance.skills.all()
            if skills:
                self.initial['skills'] = ', '.join([skill.name for skill in skills]) 