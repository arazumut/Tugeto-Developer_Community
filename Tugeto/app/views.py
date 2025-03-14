#Author : K. Umut Araz
#Date : 13.03.2025 3.17am

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm, ContactForm, NewsletterForm, EmailPreferenceForm
from .models import User, Skill, ForumCategory, ForumTopic, ForumComment, Profile, Competition, CompetitionParticipant, CompetitionAnnouncement, Newsletter, EmailPreference
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.urls import reverse
from .utils import send_html_email
from django.conf import settings
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

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

def forum_category(request, slug):
    category = get_object_or_404(ForumCategory, slug=slug)
    topics = ForumTopic.objects.filter(category=category).order_by('-created_at')
    
    
    subcategories = ForumCategory.objects.filter(parent=category)
    
    context = {
        'category': category,
        'topics': topics,
        'subcategories': subcategories,
    }
    return render(request, 'app/forum_category.html', context)

def forum_topic(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    comments = topic.comments.all()
    
    
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
def create_topic(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Konu oluşturmak için giriş yapmalısınız.')
        return redirect('app:login')
    
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
            
            
            send_forum_topic_notification(request, topic)
            
            messages.success(request, 'Konunuz başarıyla oluşturuldu.')
            return redirect('app:forum_topic', topic_id=topic.id)
        else:
            messages.error(request, 'Lütfen tüm alanları doldurun.')
    

    main_categories = ForumCategory.objects.filter(parent=None).prefetch_related('subcategories')
    
    context = {
        'main_categories': main_categories,
    }
    return render(request, 'app/create_topic.html', context)

def send_forum_topic_notification(request, topic):
    """Yeni forum konusu açıldığında e-posta bildirimi gönderir."""
    # E-posta almak isteyen kullanıcıları bul
    recipients = User.objects.filter(
        email_preferences__new_forum_topics=True,
        is_active=True
    ).exclude(email='').exclude(id=topic.author.id)  
    
    if not recipients:
        return
    
    topic_url = request.build_absolute_uri(
        reverse('app:forum_topic', kwargs={'topic_id': topic.id})
    )
    
    for recipient in recipients:
        
        unsubscribe_url = request.build_absolute_uri(
            reverse('app:email_preferences')
        )
        
        # E-posta gönder
        send_html_email(
            subject=f'Yeni Forum Konusu: {topic.title}',
            template_name='app/emails/new_forum_topic_notification.html',
            context={
                'recipient': recipient,
                'topic': topic,
                'topic_url': topic_url,
                'unsubscribe_url': unsubscribe_url,
            },
            recipient_list=[recipient.email]
        )

@login_required
def edit_topic(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    
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
    

    if request.user != topic.author and not request.user.is_staff:
        messages.error(request, 'Bu yorumu çözüm olarak işaretleme yetkiniz yok.')
        return redirect('app:forum_topic', topic_id=topic.id)
    
    
    topic.comments.filter(is_solution=True).update(is_solution=False)
    
    
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
    
    category = request.GET.get('category')
    level = request.GET.get('level')
    status = request.GET.get('status', 'active')  
    
    
    competitions = Competition.objects.all()
    
    
    if category and category != 'all':
        competitions = competitions.filter(category=category)
    if level and level != 'all':
        competitions = competitions.filter(level=level)
    
    context = {
        'competitions': competitions,
    }
    return render(request, 'app/yarisma.html', context)

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
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Kullanıcı profili oluştur
            # ... mevcut profil oluşturma kodu ...
            
            try:
                # Hoş geldiniz e-postası gönder
                profile_url = request.build_absolute_uri(reverse('app:profile'))
                send_html_email(
                    subject='Tugeto\'ya Hoş Geldiniz!',
                    template_name='app/emails/welcome_email.html',
                    context={
                        'user': user,
                        'profile_url': profile_url,
                    },
                    recipient_list=[user.email]
                )
                print(f"E-posta başarıyla gönderildi: {user.email}")
            except Exception as e:
                print(f"E-posta gönderme hatası: {e}")
            
            # Kullanıcıyı otomatik olarak giriş yap
            login(request, user)
            messages.success(request, 'Hesabınız başarıyla oluşturuldu! Hoş geldiniz!')
            return redirect('app:index')  # veya doğru URL adını kullanın
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
        
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.profile.bio = request.POST.get('bio')
        user.profile.github_url = request.POST.get('github_url')
        user.profile.linkedin_url = request.POST.get('linkedin_url')
        user.profile.website_url = request.POST.get('website_url')
        
        
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

@login_required
def create_competition(request):
    if not request.user.is_staff and request.user.user_type != 'company':
        messages.error(request, 'Yarışma oluşturma yetkiniz bulunmamaktadır.')
        return redirect('app:yarisma')
    
    if request.method == 'POST':
        # Form verilerini al
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        level = request.POST.get('level')
        prize = request.POST.get('prize')
        max_participants = request.POST.get('max_participants')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        registration_deadline = request.POST.get('registration_deadline')
        image = request.FILES.get('image')
        
        
        competition = Competition.objects.create(
            title=title,
            description=description,
            category=category,
            level=level,
            prize=prize,
            max_participants=max_participants,
            start_date=start_date,
            end_date=end_date,
            registration_deadline=registration_deadline,
            image=image,
            organizer=request.user,
            status='active'  # Varsayılan olarak aktif
        )
        
        # Yeni yarışma bildirimi gönder
        send_competition_notification(request, competition)
        
        messages.success(request, 'Yarışma başarıyla oluşturuldu!')
        return redirect('app:competition_detail', slug=competition.slug)
    

    return render(request, 'app/create_competition.html')

def send_competition_notification(request, competition):
    """Yeni yarışma oluşturulduğunda e-posta bildirimi gönderir."""
    # E-posta almak isteyen kullanıcıları bul
    recipients = User.objects.filter(
        email_preferences__new_competitions=True,
        is_active=True
    ).exclude(email='')
    
    if not recipients:
        return
    
    competition_url = request.build_absolute_uri(
        reverse('app:competition_detail', kwargs={'slug': competition.slug})
    )
    
    for recipient in recipients:
        # Her kullanıcı için abonelikten çıkma URL'si oluştur
        unsubscribe_url = request.build_absolute_uri(
            reverse('app:email_preferences')
        )
        
        # E-posta gönder
        send_html_email(
            subject=f'Yeni Yarışma: {competition.title}',
            template_name='app/emails/new_competition_notification.html',
            context={
                'recipient': recipient,
                'competition': competition,
                'competition_url': competition_url,
                'unsubscribe_url': unsubscribe_url,
            },
            recipient_list=[recipient.email]
        )

@login_required
def manage_competitions(request):
    if not request.user.is_staff and request.user.user_type != 'company':
        messages.error(request, 'Bu sayfaya erişim yetkiniz bulunmamaktadır.')
        return redirect('app:yarisma')
    
    
    if request.user.user_type == 'company':
        competitions = Competition.objects.filter(organizer=request.user)
    # Admin kullanıcıları tüm yarışmaları görebilir
    else:
        competitions = Competition.objects.all()
    
    context = {
        'competitions': competitions
    }
    return render(request, 'app/manage_competitions.html', context)

def competition_detail(request, slug):
    competition = get_object_or_404(Competition, slug=slug)
    is_participant = False
    
    if request.user.is_authenticated:
        is_participant = CompetitionParticipant.objects.filter(
            competition=competition,
            user=request.user
        ).exists()
    
    if request.method == 'POST' and request.user.is_authenticated:
        if 'join' in request.POST:

            if competition.current_participants < competition.max_participants:
                CompetitionParticipant.objects.create(
                    competition=competition,
                    user=request.user
                )
                competition.current_participants += 1
                competition.save()
                messages.success(request, 'Yarışmaya başarıyla katıldınız!')
                return redirect('app:competition_detail', slug=slug)
            else:
                messages.error(request, 'Üzgünüz, yarışma kontenjanı dolu!')
        
        elif 'submit' in request.POST and 'submission' in request.FILES:
            # Proje gönderme işlemi
            participant = CompetitionParticipant.objects.get(
                competition=competition,
                user=request.user
            )
            participant.submission = request.FILES['submission']
            participant.submission_date = timezone.now()
            participant.save()
            messages.success(request, 'Projeniz başarıyla gönderildi!')
            return redirect('app:competition_detail', slug=slug)
    
    context = {
        'competition': competition,
        'is_participant': is_participant,
        'announcements': CompetitionAnnouncement.objects.filter(competition=competition).order_by('-created_at'),
    }
    return render(request, 'app/competition_detail.html', context)

@login_required
def edit_competition(request, slug):
    competition = get_object_or_404(Competition, slug=slug)
    
    
    if request.user != competition.organizer and not request.user.is_staff:
        messages.error(request, 'Bu yarışmayı düzenleme yetkiniz bulunmamaktadır.')
        return redirect('app:competition_detail', slug=slug)
    
    if request.method == 'POST':
    
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        level = request.POST.get('level')
        prize = request.POST.get('prize')
        max_participants = request.POST.get('max_participants')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        registration_deadline = request.POST.get('registration_deadline')
        
        
        competition.title = title
        competition.description = description
        competition.category = category
        competition.level = level
        competition.prize = prize
        competition.max_participants = max_participants
        competition.start_date = start_date
        competition.end_date = end_date
        competition.registration_deadline = registration_deadline
        
        
        if 'image' in request.FILES:
            competition.image = request.FILES['image']
        
        competition.save()
        
        messages.success(request, 'Yarışma başarıyla güncellendi!')
        return redirect('app:competition_detail', slug=competition.slug)
    
    context = {
        'competition': competition,
    }
    return render(request, 'app/edit_competition.html', context)

@login_required
def delete_competition(request, slug):
    competition = get_object_or_404(Competition, slug=slug)
    
    # Yetki kontrolü - sadece organizatör veya admin silebilir
    if request.user != competition.organizer and not request.user.is_staff:
        messages.error(request, 'Bu yarışmayı silme yetkiniz bulunmamaktadır.')
        return redirect('app:competition_detail', slug=slug)
    
    if request.method == 'POST':
        competition.delete()
        messages.success(request, 'Yarışma başarıyla silindi!')
        return redirect('app:yarisma')
    
    return redirect('app:manage_competitions')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Yöneticiye bildirim e-postası gönder
            admin_email = settings.EMAIL_HOST_USER
            send_html_email(
                subject=f'Yeni İletişim Mesajı: {contact_message.subject}',
                template_name='app/emails/contact_notification.html',
                context={
                    'contact': contact_message,
                },
                recipient_list=[admin_email]
            )
            
            # Kullanıcıya teşekkür e-postası gönder
            send_html_email(
                subject='Mesajınız için teşekkürler - Tugeto',
                template_name='app/emails/contact_thank_you.html',
                context={
                    'contact': contact_message,
                },
                recipient_list=[contact_message.email]
            )
            
            messages.success(request, 'Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.')
            return redirect('app:contact')
    else:
        form = ContactForm()
    
    return render(request, 'app/contact.html', {'form': form})

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # E-posta zaten kayıtlı mı kontrol et
            if Newsletter.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Bu e-posta adresi zaten bültenimize kayıtlı.'
                })
            
            # Yeni abonelik oluştur
            newsletter = form.save()
            
            # Abonelik onay e-postası gönder
            send_html_email(
                subject='Bülten Aboneliğiniz Onaylandı - Tugeto',
                template_name='app/emails/newsletter_confirmation.html',
                context={
                    'email': email,
                },
                recipient_list=[email]
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Bülten aboneliğiniz başarıyla oluşturuldu. Teşekkürler!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Geçerli bir e-posta adresi girin.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Geçersiz istek.'
    })

def unsubscribe(request, encoded_email):
    try:
        email = force_str(urlsafe_base64_decode(encoded_email))
        newsletter = get_object_or_404(Newsletter, email=email)
        newsletter.is_active = False
        newsletter.save()
        return render(request, 'app/unsubscribe.html', {'success': True})
    except Exception:
        return render(request, 'app/unsubscribe.html', {'success': False})

@login_required
def email_preferences(request):
    preferences, created = EmailPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = EmailPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'E-posta tercihleriniz başarıyla güncellendi.')
            return redirect('app:email_preferences')
    else:
        form = EmailPreferenceForm(instance=preferences)
    
    return render(request, 'app/email_preferences.html', {'form': form})
