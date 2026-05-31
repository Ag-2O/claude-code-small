# Python テストパターン集

## フィクスチャ

```python
from unittest.mock import MagicMock

import pytest

from src.app import ApiClient, UserService


# region fixture


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Fixture that creates a mock of ApiClient."""
    return MagicMock(spec=ApiClient)


@pytest.fixture
def user_service(mock_api_client: MagicMock) -> UserService:
    """Fixture that creates an instance of UserService."""
    return UserService(api_client=mock_api_client)


# endregion
```

### セットアップとティアダウン付きフィクスチャ

```python
from collections.abc import Generator


@pytest.fixture
def database() -> Generator[Database, None, None]:
    """Fixture with setup and teardown."""
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()
```

### フィクスチャのスコープ

```python
from collections.abc import Generator
from pathlib import Path


# 関数スコープ（デフォルト）: テストごとに実行する
@pytest.fixture
def temp_file(tmp_path: Path) -> Path:
    """Provide a temporary file path."""
    return tmp_path / "test.txt"


# モジュールスコープ: モジュールごとに 1 回実行する
@pytest.fixture(scope="module")
def module_db() -> Generator[Database, None, None]:
    """Provide a shared database for all tests in the module."""
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()
```

## パラメータ化

```python
# 組み込みの input を shadow しないよう、引数名は text などにする
@pytest.mark.parametrize("text,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("PyThOn", "PYTHON"),
])
def test_uppercase(text: str, expected: str) -> None:
    """Test string uppercasing with multiple inputs."""
    assert text.upper() == expected
```

```python
# 読みやすさのためにテスト ID を追加する
@pytest.mark.parametrize("address,expected", [
    ("valid@email.com", True),
    ("invalid", False),
    ("@no-domain.com", False),
], ids=["valid-email", "missing-at", "missing-domain"])
def test_email_validation(address: str, expected: bool) -> None:
    """Test email validation with readable test IDs."""
    assert is_valid_email(address) is expected
```

## モックとパッチ

### patch デコレーター

```python
from unittest.mock import MagicMock, patch


@patch("mypackage.external_api_call")
def test_with_mock(api_call_mock: MagicMock) -> None:
    """Test with mocked external API."""
    api_call_mock.return_value = {"status": "success"}

    result = my_function()

    api_call_mock.assert_called_once()
    assert result["status"] == "success"
```

### 例外のモック

```python
@patch("mypackage.api_call")
def test_api_error_handling(api_call_mock: MagicMock) -> None:
    """Test error handling with mocked exception."""
    api_call_mock.side_effect = ConnectionError("Network error")

    with pytest.raises(ConnectionError):
        api_call()
```

### monkeypatch を使った環境変数のモック

```python
def test_get_database_url_with_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test using monkeypatch to mock environment variables."""
    monkeypatch.setenv("DB_HOST", "production-db")

    result = get_database_url()

    assert result == "postgres://user:pass@production-db:5432/db"
```

### caplog を使ったログ出力のアサーション

```python
import logging


def test_logging_output(caplog: pytest.LogCaptureFixture) -> None:
    """Test that the function logs expected messages."""
    with caplog.at_level(logging.INFO):
        some_function()

    assert "expected message" in caplog.text
```

## 例外のテスト

```python
def test_divide_by_zero() -> None:
    """Test that dividing by zero raises ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)


def test_custom_exception_details() -> None:
    """Test custom exception with attributes."""
    with pytest.raises(CustomError) as exc_info:
        raise CustomError("error", code=400)

    assert exc_info.value.code == 400
```

## ファイル操作のテスト

```python
from pathlib import Path


def test_with_tmp_path(tmp_path: Path) -> None:
    """Test using pytest's built-in temp path fixture."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    result = process_file(test_file)

    assert result == "hello world"
```

## テストクラスの構造例

```python
from unittest.mock import MagicMock

import pytest

from src.app import ApiClient, UserService, get_database_url


# region fixture


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Fixture that creates a mock of ApiClient."""
    return MagicMock(spec=ApiClient)


@pytest.fixture
def user_service(mock_api_client: MagicMock) -> UserService:
    """Fixture that creates an instance of UserService."""
    return UserService(api_client=mock_api_client)


# endregion


# region UserService


class TestUserService:
    """Test group regarding the UserService class."""

    def test_get_user_name_success(
        self,
        user_service: UserService,
        mock_api_client: MagicMock,
    ) -> None:
        """Success scenario test using MagicMock."""
        mock_api_client.get_user_data.return_value = {"id": 1, "name": "Taro"}

        result = user_service.get_user_name(1)

        assert result == "Taro"
        mock_api_client.get_user_data.assert_called_once_with(1)

    def test_get_user_name_not_found(
        self,
        user_service: UserService,
        mock_api_client: MagicMock,
    ) -> None:
        """Test for when data is not found (empty response)."""
        mock_api_client.get_user_data.return_value = {}

        result = user_service.get_user_name(999)

        assert result == "Unknown"


# endregion


# region EnvironmentConfig


class TestEnvironmentConfig:
    """Test group regarding environment configuration and settings retrieval."""

    def test_get_database_url_default(self) -> None:
        """Test without using monkeypatch (verifying default value)."""
        assert get_database_url() == "postgres://user:pass@localhost:5432/db"

    def test_get_database_url_with_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test using monkeypatch to mock environment variables."""
        monkeypatch.setenv("DB_HOST", "production-db")

        result = get_database_url()

        assert result == "postgres://user:pass@production-db:5432/db"


# endregion
```

## テストコマンド

```bash
uv run pytest                                       # すべてのテストを実行する
uv run pytest tests/test_utils.py                   # 特定のファイルを実行する
uv run pytest -k "test_user"                        # 名前でフィルタリングする
uv run pytest -x                                    # 最初の失敗で停止する
uv run pytest --lf                                  # 前回失敗したテストのみ実行する
uv run pytest --cov=src --cov-report=term-missing   # カバレッジ付きで実行する
```
