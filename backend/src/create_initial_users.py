#!/usr/bin/env python
"""
初期ユーザー作成スクリプト
Docker環境での初回セットアップ時に実行
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 管理者ユーザー
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'is_staff': True,
        'is_superuser': True,
    }
)
admin.set_password('admin123')
admin.save()
print(f"Admin user {'created' if created else 'updated'}: admin / admin123")

# テストユーザー
naoki, created = User.objects.get_or_create(
    username='naoki',
    defaults={'email': 'naoki@example.com'}
)
naoki.set_password('password123')
naoki.save()
print(f"Test user {'created' if created else 'updated'}: naoki / password123")

print("\n✓ Initial users ready!")
