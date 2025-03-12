#!/bin/bash

# Gerekli paketleri yükle
echo "Gerekli paketler yükleniyor..."
pip install -r requirements.txt

# Veritabanı migrasyonlarını oluştur
echo "Veritabanı migrasyonları oluşturuluyor..."
python manage.py makemigrations

# Migrasyonları uygula
echo "Migrasyonlar uygulanıyor..."
python manage.py migrate

# Statik dosyaları topla
echo "Statik dosyalar toplanıyor..."
python manage.py collectstatic --noinput

# Süper kullanıcı oluştur
echo "Süper kullanıcı oluşturuluyor..."
python manage.py createsuperuser

# Sunucuyu başlat
echo "Sunucu başlatılıyor..."
python manage.py runserver 