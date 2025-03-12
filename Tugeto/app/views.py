from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from .models import User, Skill

# Create your views here.
def index(request):
    return render(request, 'app/index.html')

def forum(request):
    return render(request, 'app/forum.html')

def yarisma(request):
    return render(request, 'app/yarisma.html')

def hakkimizda(request):
    return render(request, 'app/hakkimizda.html')

def iletisim(request):
    return render(request, 'app/iletisim.html')

def privacy_policy(request):
    return render(request, 'app/privacy_policy.html')

def terms(request):
    return render(request, 'app/terms.html')

def login_view(request):
    """Kullanıcı giriş görünümü"""
    if request.user.is_authenticated:
        return redirect('app:index')
    
    if request.method == 'POST':
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
    else:
        form = UserLoginForm()
    
    return render(request, 'app/login.html', {'form': form})

def register_view(request):
    """Kullanıcı kayıt görünümü"""
    if request.user.is_authenticated:
        return redirect('app:index')
    
    if request.method == 'POST':
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
    else:
        form = UserRegisterForm()
    
    return render(request, 'app/register.html', {'form': form})

@login_required
def logout_view(request):
    """Kullanıcı çıkış görünümü"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('app:login')

@login_required
def profile_view(request):
    """Kullanıcı profil görünümü"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Profil bilgilerini güncelle
            if hasattr(user, 'profile'):
                user.profile.user_type = form.cleaned_data.get('user_type')
                user.profile.save()
            
            # Kullanıcı yeteneklerini güncelle
            skills = form.cleaned_data.get('skills')
            if skills:
                user.skills.clear()
                for skill_name in skills.split(','):
                    skill_name = skill_name.strip()
                    if skill_name:
                        skill, created = Skill.objects.get_or_create(name=skill_name)
                        user.skills.add(skill)
            
            user.save()
            
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            return redirect('app:profile')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'app/profile.html', {'form': form})
