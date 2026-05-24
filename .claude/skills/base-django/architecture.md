# Django アーキテクチャ & セキュリティ

スケーラブルで保守しやすいアプリケーションのための、本番グレードの Django アーキテクチャパターンとセキュリティガイドライン。

## プロジェクト構造

```text
myproject/
├── config/
│   ├── settings/
│   │   ├── base.py          # 共通設定
│   │   ├── development.py   # 開発環境設定
│   │   ├── production.py    # 本番環境設定
│   │   └── test.py          # テスト設定
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
└── apps/
    ├── users/
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   ├── urls.py
    │   ├── permissions.py
    │   ├── filters.py
    │   ├── services.py
    │   └── tests/
    └── products/
        └── ...
```

## 設定

### 設定ファイル分割パターン

```python
# config/settings/base.py
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env(DEBUG=(bool, False))

SECRET_KEY = env('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY environment variable is required')
DEBUG = False
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'apps.users',
    'apps.products',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
AUTH_USER_MODEL = 'users.User'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

```python
# config/settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

```python
# config/settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# HTTPS & セキュリティヘッダー
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 3600 * 24 * 7

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {'level': 'WARNING', 'class': 'logging.FileHandler',
                 'filename': '/var/log/django/django.log'},
    },
    'loggers': {
        'django': {'handlers': ['file'], 'level': 'WARNING', 'propagate': True},
        'django.security': {'handlers': ['file'], 'level': 'WARNING', 'propagate': True},
        'django.request': {'handlers': ['file'], 'level': 'ERROR', 'propagate': False},
    },
}
```

## モデル設計

### カスタムユーザーモデル

プロジェクト開始時に必ず定義する — 後から変更するとコストが高い。

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
```

### モデルのベストプラクティス

```python
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE,
                                 related_name='products')
    tags = models.ManyToManyField('Tag', blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', 'is_active']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name='price_non_negative')
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

### カスタム QuerySet & Manager

```python
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_relations(self):
        return self.select_related('category').prefetch_related('tags')

    def in_stock(self):
        return self.filter(stock__gt=0)

    def search(self, query):
        return self.filter(
            models.Q(name__icontains=query) | models.Q(description__icontains=query)
        )

class ProductManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

class Product(models.Model):
    # ... フィールド定義 ...
    objects = ProductManager.from_queryset(ProductQuerySet)()

# 使用例
Product.objects.active().with_relations().in_stock()
```

## Django REST Framework

### シリアライザー

```python
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'discount_price',
                  'stock', 'category_name', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

    def get_discount_price(self, obj):
        if hasattr(obj, 'discount') and obj.discount:
            return obj.price * (1 - obj.discount.percent / 100)
        return obj.price

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password],
                                     style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True,
                                             style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords didn't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
```

### ViewSet

```python
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').prefetch_related('tags')
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = self.queryset.filter(is_featured=True)[:10]
        return Response(self.get_serializer(featured, many=True).data)

    @action(detail=False, methods=['get'])
    def my_products(self, request):
        products = self.queryset.filter(created_by=request.user)
        page = self.paginate_queryset(products)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)
```

## サービス層

```python
# apps/orders/services.py
from django.db import transaction

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(user, cart) -> Order:
        order = Order.objects.create(user=user, total_price=cart.total_price)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order, product=item.product,
                quantity=item.quantity, price=item.product.price
            )
        cart.items.all().delete()
        return order

    @staticmethod
    def process_payment(order, payment_data: dict) -> bool:
        payment = PaymentGateway.charge(amount=order.total_price,
                                        token=payment_data['token'])
        if payment.success:
            order.status = Order.Status.PAID
            order.save()
            OrderService.send_confirmation_email(order)
            return True
        return False
```

## キャッシュ

```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# ビューレベルのキャッシュ（15分）
@method_decorator(cache_page(60 * 15), name='dispatch')
class ProductListView(generic.ListView):
    model = Product

# 低レベルキャッシュ
def get_featured_products():
    cache_key = 'featured_products'
    products = cache.get(cache_key)
    if products is None:
        products = list(Product.objects.filter(is_featured=True))
        cache.set(cache_key, products, timeout=60 * 15)
    return products
```

## シグナル

```python
# apps/users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# apps/users/apps.py
class UsersConfig(AppConfig):
    name = 'apps.users'

    def ready(self):
        import apps.users.signals
```

## ミドルウェア

```python
import time
from django.utils.deprecation import MiddlewareMixin

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f'{request.method} {request.path} - {response.status_code} - {duration:.3f}s')
        return response

class SecurityHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Content-Security-Policy'] = "default-src 'self'"
        return response
```

## 認可

### カスタムパーミッション（DRF）

```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
```

### ロールベースアクセス制御

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
        ('user', 'Regular User'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_moderator(self):
        return self.role in ['admin', 'moderator']
```

## SQL インジェクション対策

```python
# 良い例: ORM がパラメータを自動エスケープする
User.objects.get(username=username)
User.objects.filter(email__iexact=email)
User.objects.filter(Q(username__icontains=q) | Q(email__icontains=q))

# 良い例: 生 SQL が必要な場合は必ずパラメータを使う
User.objects.raw('SELECT * FROM users WHERE email = %s', [email])

# 悪い例: ユーザー入力を直接展開しない
User.objects.raw(f'SELECT * FROM users WHERE username = {username}')  # 脆弱！
```

## XSS 対策

```python
from django.utils.html import escape, format_html

# 良い例: format_html が変数を自動エスケープする
def greet_user(username):
    return format_html('<span class="user">{}</span>', username)

# 悪い例: サニタイズされていないユーザー入力を safe にしない
from django.utils.safestring import mark_safe
mark_safe(user_input)  # 脆弱！
```

```django
{# Django はデフォルトで自動エスケープする #}
{{ user_input }}

{# JavaScript コンテキスト #}
<script>var username = {{ username|escapejs }};</script>
```

## ファイルアップロードのセキュリティ

```python
import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.pdf']:
        raise ValidationError('Unsupported file extension.')

def validate_file_size(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError('File too large. Max size is 5MB.')

class Document(models.Model):
    file = models.FileField(upload_to='documents/',
                            validators=[validate_file_extension, validate_file_size])
```

## API セキュリティ（DRF）

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
}
```

## パフォーマンス最適化

```python
# select_related / prefetch_related で N+1 を回避する
products = Product.objects.select_related('category').prefetch_related('tags')

# バルク操作
Product.objects.bulk_create([Product(name=f'P{i}', price=10) for i in range(1000)])

products = list(Product.objects.all()[:100])
for p in products:
    p.is_active = True
Product.objects.bulk_update(products, ['is_active'])
```

## クイックリファレンス

| パターン               | 説明                                                       |
| ---------------------- | ---------------------------------------------------------- |
| 設定ファイル分割       | 開発・本番・テストで設定を分離する                         |
| `AUTH_USER_MODEL`      | プロジェクト開始時に設定する。後から変更するとコストが高い |
| カスタム QuerySet      | 再利用・チェーン可能なクエリメソッド                       |
| サービス層             | ビジネスロジックをビューの外に分離する                     |
| `select_related`       | 外部キーの N+1 問題を解消する                              |
| `prefetch_related`     | 多対多の N+1 問題を解消する                                |
| `bulk_create/update`   | 効率的なバッチ DB 操作                                     |
| キャッシュ優先         | コストの高い処理はキャッシュする                           |
| `IsOwnerOrReadOnly`    | オブジェクトレベルの DRF パーミッション                    |
| `Argon2PasswordHasher` | より強力なパスワードハッシュ                               |
| `SECURE_SSL_REDIRECT`  | 本番環境で HTTPS を強制する                                |
| `format_html`          | 変数を含む安全な HTML 生成                                 |

セキュリティと構造は簡潔さより優先する。保守しやすいコードを目指す。
