#Author : K. Umut Araz
#Date : 13.03.2025 3.17am

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from .models import User, Skill, ForumCategory, ForumTopic, ForumComment, Profile
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def index(request):
    return render(request, 'app/index.html')

def forum(request):
    categories = ForumCategory.objects.filter(parent=None).order_by('order')
    recent_topics = ForumTopic.objects.order_by('-created_at')[:5]
    popular_topics = ForumTopic.objects.annotate(comment_count=Count('comments')).order_by('-comment_count')[:5]
    
    context = {
        'categories': categories,
        'recent_topics': recent_topics,
        'popular_topics': popular_topics,
    }
    return render(request, 'app/forum.html', context)

def forum_category(request, category_slug):
    category = get_object_or_404(ForumCategory, slug=category_slug)
    subcategories = ForumCategory.objects.filter(parent=category)
    topics = ForumTopic.objects.filter(category=category).order_by('-is_pinned', '-created_at')
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'topics': topics,
    }
    return render(request, 'app/forum_category.html', context)

def forum_topic(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    comments = topic.comments.all()
    
    # Görüntülenme sayısını artır
    topic.views += 1
    topic.save()
    
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            ForumComment.objects.create(
                topic=topic,
                author=request.user,
                content=content
            )
            messages.success(request, 'Yorumunuz başarıyla eklendi.')
            return redirect('app:forum_topic', topic_id=topic.id)
    
    context = {
        'topic': topic,
        'comments': comments,
    }
    return render(request, 'app/forum_topic.html', context)

@login_required
def create_topic(request, category_slug=None):
    if category_slug:
        category = get_object_or_404(ForumCategory, slug=category_slug)
    else:
        category = None
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        
        if title and content and category_id:
            category = get_object_or_404(ForumCategory, id=category_id)
            topic = ForumTopic.objects.create(
                title=title,
                content=content,
                category=category,
                author=request.user
            )
            messages.success(request, 'Konunuz başarıyla oluşturuldu.')
            return redirect('app:forum_topic', topic_id=topic.id)
        else:
            messages.error(request, 'Lütfen tüm alanları doldurun.')
    
    categories = ForumCategory.objects.all()
    context = {
        'categories': categories,
        'selected_category': category,
    }
    return render(request, 'app/create_topic.html', context)

@login_required
def edit_topic(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    # Sadece konu sahibi veya admin düzenleyebilir
    if request.user != topic.author and not request.user.is_staff:
        messages.error(request, 'Bu konuyu düzenleme yetkiniz yok.')
        return redirect('app:forum_topic', topic_id=topic.id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        
        if title and content and category_id:
            category = get_object_or_404(ForumCategory, id=category_id)
            topic.title = title
            topic.content = content
            topic.category = category
            topic.save()
            messages.success(request, 'Konunuz başarıyla güncellendi.')
            return redirect('app:forum_topic', topic_id=topic.id)
        else:
            messages.error(request, 'Lütfen tüm alanları doldurun.')
    
    categories = ForumCategory.objects.all()
    context = {
        'topic': topic,
        'categories': categories,
    }
    return render(request, 'app/edit_topic.html', context)

@login_required
def delete_topic(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    # Sadece konu sahibi veya admin silebilir
    if request.user != topic.author and not request.user.is_staff:
        messages.error(request, 'Bu konuyu silme yetkiniz yok.')
        return redirect('app:forum_topic', topic_id=topic.id)
    
    if request.method == 'POST':
        category = topic.category
        topic.delete()
        messages.success(request, 'Konunuz başarıyla silindi.')
        return redirect('app:forum_category', category_slug=category.slug)
    
    context = {
        'topic': topic,
    }
    return render(request, 'app/delete_topic.html', context)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
    
    # Sadece yorum sahibi veya admin düzenleyebilir
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, 'Bu yorumu düzenleme yetkiniz yok.')
        return redirect('app:forum_topic', topic_id=comment.topic.id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            comment.content = content
            comment.save()
            messages.success(request, 'Yorumunuz başarıyla güncellendi.')
            return redirect('app:forum_topic', topic_id=comment.topic.id)
        else:
            messages.error(request, 'Lütfen yorum içeriğini doldurun.')
    
    context = {
        'comment': comment,
    }
    return render(request, 'app/edit_comment.html', context)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
    
    # Sadece yorum sahibi veya admin silebilir
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, 'Bu yorumu silme yetkiniz yok.')
        return redirect('app:forum_topic', topic_id=comment.topic.id)
    
    if request.method == 'POST':
        topic_id = comment.topic.id
        comment.delete()
        messages.success(request, 'Yorumunuz başarıyla silindi.')
        return redirect('app:forum_topic', topic_id=topic_id)
    
    context = {
        'comment': comment,
    }
    return render(request, 'app/delete_comment.html', context)

@login_required
def mark_solution(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
    topic = comment.topic
    
    # Sadece konu sahibi veya admin çözüm olarak işaretleyebilir
    if request.user != topic.author and not request.user.is_staff:
        messages.error(request, 'Bu yorumu çözüm olarak işaretleme yetkiniz yok.')
        return redirect('app:forum_topic', topic_id=topic.id)
    
    # Diğer çözümleri kaldır
    topic.comments.filter(is_solution=True).update(is_solution=False)
    
    # Bu yorumu çözüm olarak işaretle
    comment.is_solution = True
    comment.save()
    
    messages.success(request, 'Yorum çözüm olarak işaretlendi.')
    return redirect('app:forum_topic', topic_id=topic.id)

def search_forum(request):
    query = request.GET.get('q', '')
    
    if query:
        topics = ForumTopic.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')
        
        comments = ForumComment.objects.filter(
            content__icontains=query
        ).order_by('-created_at')
    else:
        topics = ForumTopic.objects.none()
        comments = ForumComment.objects.none()
    
    context = {
        'query': query,
        'topics': topics,
        'comments': comments,
    }
    return render(request, 'app/search_results.html', context)

def yarisma(request):
    return render(request, 'app/yarisma.html')

def hakkimizda(request):
    return render(request, 'app/hakkimizda.html')

def iletisim(request):
    return render(request, 'app/iletisim.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Kullanıcının profili yoksa oluştur
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                Profile.objects.create(user=user)
            
            if not remember_me:
                request.session.set_expiry(0)
            
            messages.success(request, f'Hoş geldiniz, {user.first_name}!')
            return redirect('app:index')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
            return redirect('app:login')
    
    return render(request, 'app/login.html')

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
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('app:index')

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

def privacy_policy(request):
    return render(request, 'app/privacy_policy.html')

def terms(request):
    return render(request, 'app/terms.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        # Profil bilgilerini güncelle
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.profile.bio = request.POST.get('bio')
        user.profile.github_url = request.POST.get('github_url')
        user.profile.linkedin_url = request.POST.get('linkedin_url')
        user.profile.website_url = request.POST.get('website_url')
        
        # Profil fotoğrafını güncelle
        if 'avatar' in request.FILES:
            user.profile.avatar = request.FILES['avatar']
        
        user.save()
        user.profile.save()
        
        messages.success(request, 'Profil bilgileriniz başarıyla güncellendi.')
        return redirect('app:profile')
    
    return redirect('app:profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Şifre kontrolü
        if not request.user.check_password(current_password):
            messages.error(request, 'Mevcut şifreniz yanlış.')
            return redirect('app:profile')
        
        # Yeni şifre kontrolü
        if new_password1 != new_password2:
            messages.error(request, 'Yeni şifreler eşleşmiyor.')
            return redirect('app:profile')
        
        # Şifreyi güncelle
        request.user.set_password(new_password1)
        request.user.save()
        
        messages.success(request, 'Şifreniz başarıyla değiştirildi. Lütfen tekrar giriş yapın.')
        return redirect('app:login')
    
    return redirect('app:profile')
