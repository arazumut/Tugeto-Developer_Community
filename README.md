# 🚀 Tugeto - Yazılım Topluluğu Platformu

<div align="center">
  <img src="app/static/app/assets/Adsız_tasarım-removebg-preview.png" alt="Tugeto Logo" width="200">
  <br>
  <p><i>Yazılım dünyasında yenilikçi fikirleri destekleyen ve geliştiren topluluk platformu</i></p>
</div>

## 📋 Proje Hakkında

Tugeto, yazılım geliştiricileri, öğrencileri ve teknoloji meraklılarını bir araya getiren interaktif bir topluluk platformudur. Kullanıcılar forum üzerinden bilgi paylaşabilir, yarışmalara katılabilir ve yazılım dünyasındaki yolculuklarında birbirlerine destek olabilirler.

## ✨ Özellikler

- 👥 **Kullanıcı Yönetimi**: Kayıt, giriş ve profil yönetimi
- 💬 **Forum**: Kategorilere ayrılmış tartışma alanları
- 🏆 **Yarışmalar**: Çeşitli kategorilerde düzenlenen kodlama yarışmaları
- 📝 **Blog**: Yazılım ve teknoloji ile ilgili makaleler
- 📱 **Responsive Tasarım**: Tüm cihazlarda sorunsuz çalışan modern arayüz

## 🛠️ Teknolojiler

- **Backend**: Django 5.1.6
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Veritabanı**: PostgreSQL
- **Deployment**: Docker, Nginx
- **Diğer**: RESTful API, AJAX

## 🚀 Kurulum

### Gereksinimler

- Python 3.10+
- PostgreSQL
- pip

### Adımlar

1. Repoyu klonlayın:
   ```bash
   git clone https://github.com/kullaniciadi/tugeto.git
   cd tugeto
   ```

2. Sanal ortam oluşturun ve aktifleştirin:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Veritabanını oluşturun:
   ```bash
   python manage.py migrate
   ```

5. Sunucuyu başlatın:
   ```bash
   python manage.py runserver
   ```

6. Tarayıcınızda `http://127.0.0.1:8000` adresine gidin.

## 📦 Proje Yapısı

```
tugeto/
├── app/                    # Ana uygulama
│   ├── migrations/         # Veritabanı migrasyonları
│   ├── static/             # Statik dosyalar (CSS, JS, resimler)
│   ├── templates/          # HTML şablonları
│   ├── admin.py            # Admin panel yapılandırması
│   ├── models.py           # Veritabanı modelleri
│   ├── views.py            # Görünüm fonksiyonları
│   └── urls.py             # URL yapılandırması
├── Tugeto/                 # Proje ayarları
│   ├── settings.py         # Proje ayarları
│   ├── urls.py             # Ana URL yapılandırması
│   └── wsgi.py             # WSGI yapılandırması
├── manage.py               # Django yönetim aracı
└── requirements.txt        # Bağımlılıklar
```

## 📸 Ekran Görüntüleri

<div align="center">
  <img src="screenshots/anasayfa.png" alt="Ana Sayfa" width="400">
  <img src="screenshots/forum.png" alt="Forum" width="400">
  <img src="screenshots/yarisma.png" alt="Yarışmalar" width="400">
  <img src="screenshots/profil.png" alt="Profil" width="400">
</div>

## 🤝 Katkıda Bulunma

1. Bu repoyu forklayın
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inize push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun


<div align="center">
  <p>Türkiye'de geliştirilmiştir</p>
</div>
