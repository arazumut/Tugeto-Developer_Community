from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse_lazy
from .models import User, Skill
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm

class RegisterView(View):
    """
    Kullanıcı kayıt görünümü.
    """
    def get(self, request):
        # Kullanıcı zaten giriş yapmışsa ana sayfaya yönlendir
        if request.user.is_authenticated:
            return redirect('app:index')
        
        form = UserRegisterForm()
        return render(request, 'app/register.html', {'form': form})
    
    def post(self, request):
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            # Kullanıcı tipini ve yetenekleri profil modeline kaydet
            user_type = form.cleaned_data.get('user_type')
            if hasattr(user, 'profile'):
                user.profile.user_type = user_type
                user.profile.save()
            
            # Kullanıcı yeteneklerini ekle
            skills = form.cleaned_data.get('skills')
            if skills:
                for skill_name in skills.split(','):
                    skill_name = skill_name.strip()
                    if skill_name:
                        skill, created = Skill.objects.get_or_create(name=skill_name)
                        user.skills.add(skill)
            
            # Kullanıcıyı otomatik olarak giriş yap
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Hesabınız başarıyla oluşturuldu! Hoş geldiniz, {user.first_name}!')
            return redirect('app:index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return render(request, 'app/register.html', {'form': form})

class LoginView(View):
    """
    Kullanıcı giriş görünümü.
    """
    def get(self, request):
        # Kullanıcı zaten giriş yapmışsa ana sayfaya yönlendir
        if request.user.is_authenticated:
            return redirect('app:index')
        
        form = UserLoginForm()
        return render(request, 'app/login.html', {'form': form})
    
    def post(self, request):
        form = UserLoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Eğer "Beni Hatırla" seçeneği işaretlenmemişse, oturum tarayıcı kapandığında sona erecek
                if not remember_me:
                    request.session.set_expiry(0)
                
                messages.success(request, f'Hoş geldiniz, {user.first_name}!')
                
                # Eğer next parametresi varsa, o sayfaya yönlendir
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                
                return redirect('app:index')
            else:
                messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
        else:
            messages.error(request, 'Lütfen geçerli bilgiler girin.')
        
        return render(request, 'app/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Kullanıcı çıkış görünümü.
    """
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('app:login')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """
    Kullanıcı profil görünümü.
    """
    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, 'app/profile.html', {'form': form})
    
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            user = form.save(commit=False)
            
            # Profil bilgilerini güncelle
            if hasattr(user, 'profile'):
                user.profile.user_type = form.cleaned_data.get('user_type')
                
                skills = form.cleaned_data.get('skills')
                if skills:
                    user.skills.clear()
                    for skill_name in skills.split(','):
                        skill_name = skill_name.strip()
                        if skill_name:
                            skill, created = Skill.objects.get_or_create(name=skill_name)
                            user.skills.add(skill)
                
                user.profile.save()
            
            user.save()
            
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            return redirect('app:profile')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
        
        return render(request, 'app/profile.html', {'form': form}) 