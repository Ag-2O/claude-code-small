# Django テスト & 検証

Django アプリケーションのテスト駆動開発、テストインフラ、デプロイ前検証。

## TDD ワークフロー

### Red-Green-Refactor サイクル

```python
# ステップ1: RED — 失敗するテストを書く
def test_user_creation():
    user = User.objects.create_user(email='test@example.com', password='testpass123')
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')
    assert not user.is_staff

# ステップ2: GREEN — テストを通過させる（モデル・ファクトリを実装する）
# ステップ3: REFACTOR — テストを通したままコードを改善する
```

## セットアップ

### pytest 設定

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --reuse-db
    --nomigrations
    --cov=apps
    --cov-report=html
    --cov-report=term-missing
    --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### テスト設定

```python
# config/settings/test.py
from .base import *

DEBUG = True
DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
}

class DisableMigrations:
    def __contains__(self, item): return True
    def __getitem__(self, item): return None

MIGRATION_MODULES = DisableMigrations()
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

### conftest.py

```python
# tests/conftest.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com', password='testpass123', username='testuser'
    )

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email='admin@example.com', password='adminpass123', username='admin'
    )

@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def authenticated_api_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
```

## Factory Boy

```python
# tests/factories.py
import factory
from factory import fuzzy
from django.contrib.auth import get_user_model
from apps.products.models import Product, Category

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('sentence', nb_words=3)
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    price = fuzzy.FuzzyDecimal(10.00, 1000.00, 2)
    stock = fuzzy.FuzzyInteger(0, 100)
    is_active = True
    category = factory.SubFactory(CategoryFactory)
    created_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for tag in extracted:
            self.tags.add(tag)
```

## モデルテスト

```python
# tests/test_models.py
import pytest
from django.core.exceptions import ValidationError
from tests.factories import UserFactory, ProductFactory

class TestUserModel:
    def test_create_user(self, db):
        user = UserFactory(email='test@example.com')
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert not user.is_staff

    def test_user_str(self, db):
        user = UserFactory(email='test@example.com')
        assert str(user) == 'test@example.com'

class TestProductModel:
    def test_product_creation(self, db):
        product = ProductFactory()
        assert product.id is not None
        assert product.is_active is True

    def test_slug_generation(self, db):
        product = ProductFactory(name='Test Product')
        assert product.slug == 'test-product'

    def test_price_validation(self, db):
        product = ProductFactory(price=-10)
        with pytest.raises(ValidationError):
            product.full_clean()

    def test_manager_active(self, db):
        ProductFactory.create_batch(5, is_active=True)
        ProductFactory.create_batch(3, is_active=False)
        assert Product.objects.active().count() == 5
```

## ビューテスト

```python
# tests/test_views.py
import pytest
from django.urls import reverse
from tests.factories import ProductFactory

class TestProductViews:
    def test_product_list(self, client, db):
        ProductFactory.create_batch(10)
        response = client.get(reverse('products:list'))
        assert response.status_code == 200
        assert len(response.context['products']) == 10

    def test_create_requires_login(self, client, db):
        response = client.get(reverse('products:create'))
        assert response.status_code == 302
        assert response.url.startswith('/accounts/login/')

    def test_create_post(self, authenticated_client, db, category):
        data = {'name': 'Test', 'description': 'Desc', 'price': '99.99',
                'stock': 10, 'category': category.id}
        response = authenticated_client.post(reverse('products:create'), data)
        assert response.status_code == 302
        assert Product.objects.filter(name='Test').exists()
```

## DRF API テスト

```python
# tests/test_api.py
import pytest
from rest_framework import status
from django.urls import reverse
from tests.factories import ProductFactory

class TestProductAPI:
    def test_list_products(self, api_client, db):
        ProductFactory.create_batch(10)
        response = api_client.get(reverse('api:product-list'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10

    def test_create_unauthorized(self, api_client, db):
        response = api_client.post(reverse('api:product-list'), {'name': 'Test'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_authorized(self, authenticated_api_client, db):
        data = {'name': 'Test', 'description': 'Desc', 'price': '99.99', 'stock': 10}
        response = authenticated_api_client.post(reverse('api:product-list'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test'

    def test_filter_by_price(self, api_client, db):
        ProductFactory(price=50)
        ProductFactory(price=150)
        response = api_client.get(reverse('api:product-list'), {'price_min': 100})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
```

## モック

```python
from unittest.mock import patch
from django.core import mail
from django.test import override_settings

# 外部サービスのモック
class TestPayment:
    @patch('apps.payments.services.stripe')
    def test_successful_payment(self, mock_stripe, client, user, product):
        mock_stripe.Charge.create.return_value = {'id': 'ch_123', 'status': 'succeeded'}
        client.force_login(user)
        response = client.post(reverse('payments:process'),
                               {'product_id': product.id, 'token': 'tok_visa'})
        assert response.status_code == 302
        mock_stripe.Charge.create.assert_called_once()

# メールのモック
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_order_confirmation_email(db, order):
    order.send_confirmation_email()
    assert len(mail.outbox) == 1
    assert 'Order Confirmation' in mail.outbox[0].subject
```

## 検証チェックリスト

PR 前・大きな変更後・デプロイ前に実行する。

### フェーズ 1: コード品質

```bash
mypy . --config-file pyproject.toml
ruff check . --fix
black . --check
isort . --check-only
python manage.py check --deploy
```

### フェーズ 2: マイグレーション

```bash
python manage.py showmigrations
python manage.py makemigrations --check   # 未追跡の変更があると失敗する
python manage.py migrate --plan
```

### フェーズ 3: テスト & カバレッジ

```bash
pytest --cov=apps --cov-report=html --cov-report=term-missing --reuse-db
pytest -m "not slow"       # 低速テストをスキップする
pytest -m integration      # 結合テストのみ実行する
```

| コンポーネント | 目標 |
| -------------- | ---- |
| モデル | 90%以上 |
| シリアライザー | 85%以上 |
| ビュー | 80%以上 |
| サービス | 90%以上 |
| 全体 | 80%以上 |

### フェーズ 4: セキュリティスキャン

```bash
pip-audit
bandit -r . -f json -o bandit-report.json
python manage.py check --deploy
```

### フェーズ 5: 差分レビュー

```bash
git diff | grep -E "print\(|import pdb|DEBUG = True|TODO|FIXME"
```

- [ ] デバッグ文がない（print, pdb, breakpoint()）
- [ ] ハードコードされた秘密情報・認証情報がない
- [ ] モデル変更に対応するマイグレーションが含まれている
- [ ] 必要な箇所でトランザクション管理がされている

## デプロイ前チェックリスト

- [ ] 全テスト通過、カバレッジ 80% 以上
- [ ] セキュリティ脆弱性なし（`pip-audit` クリーン）
- [ ] 未適用のマイグレーションなし
- [ ] 本番設定で `DEBUG = False`
- [ ] `SECRET_KEY` が環境変数で設定されている
- [ ] `ALLOWED_HOSTS` が設定されている
- [ ] HTTPS/SSL が設定されている
- [ ] 静的ファイルを収集済み（`collectstatic`）
- [ ] ロギングが設定されている
- [ ] エラー監視が設定されている（Sentry 等）
- [ ] Redis/キャッシュバックエンドに接続できる
- [ ] Celery ワーカーが起動している（該当する場合）

## CI 設定

```yaml
# .github/workflows/django.yml
name: Django CI
on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: 依存関係のインストール
        run: pip install -r requirements.txt ruff black mypy pytest pytest-django pytest-cov bandit pip-audit

      - name: コード品質チェック
        run: |
          ruff check .
          black . --check
          mypy .

      - name: セキュリティスキャン
        run: bandit -r . && pip-audit

      - name: テスト実行
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
          DJANGO_SECRET_KEY: test-secret-key
        run: pytest --cov=apps --cov-report=xml
```

## クイックリファレンス

| 項目 | コマンド / 備考 |
| ---- | --------------- |
| テスト実行 | `pytest --cov=apps` |
| 低速テストをスキップ | `pytest -m "not slow"` |
| 型チェック | `mypy .` |
| リント | `ruff check .` |
| マイグレーション確認 | `python manage.py makemigrations --check` |
| セキュリティ | `pip-audit && bandit -r .` |
| Django チェック | `python manage.py check --deploy` |
| DB フィクスチャ | `db`（pytest-django） |
| 認証バイパス | `force_authenticate()` / `force_login()` |
| メール確認 | `mail.outbox` |
| バッチ作成 | `Factory.create_batch(n)` |

テストはドキュメントでもある。シンプルで読みやすく、保守しやすいテストを書く。
