# Python コーディングパターン集

## 基本原則

### 1. 読みやすさを優先する

Python は何より読みやすさを重視する。コードは明確で理解しやすくあるべき。

```python
# 良い例: 明確で読みやすい
def get_active_users(users: list[User]) -> list[User]:
    """Return only active users from the provided list."""
    return [user for user in users if user.is_active]


# 悪い例: 巧妙だが不明瞭
def get_active_users(u):
    return [x for x in u if x.a]
```

### 2. 暗黙より明示を好む

コードが何をしているかを明確にする。

```python
# 良い例: 明示的な設定
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

### 3. EAFP（許可を求めるより許しを求める方が簡単）

Python では条件チェックより例外処理を好む。

```python
from typing import TypeVar

T = TypeVar("T")


# 良い例: EAFP スタイル（Pythonic）
def get_value(dictionary: dict[str, T], key: str, default: T) -> T:
    """Get a value from a dictionary with a default fallback."""
    try:
        return dictionary[key]
    except KeyError:
        return default
```

## 型ヒント

### 基本的な型アノテーション（Python 3.11+）

```python
def process_user(
    user_id: str,
    name: str,
    active: bool = True,
) -> User | None:
    """Process a user and return the updated User or None."""
    if not active:
        return None
    return User(user_id, name)
```

### 型エイリアスと TypeVar

```python
from typing import TypeVar

JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

T = TypeVar("T")


def first(items: list[T]) -> T | None:
    """Return the first item or None if list is empty."""
    return items[0] if items else None
```

### Protocol を使った構造的サブタイピング

```python
from typing import Protocol


class Renderable(Protocol):
    def render(self) -> str:
        """Render the object to a string."""


def render_all(items: list[Renderable]) -> str:
    """Render all items that implement the Renderable protocol."""
    return "\n".join(item.render() for item in items)
```

### collections.abc から Callable と Iterator をインポートする

```python
from collections.abc import Callable, Iterator


def apply(func: Callable[[int], int], values: list[int]) -> list[int]:
    """Apply a function to each value."""
    return [func(v) for v in values]


def count_up(start: int) -> Iterator[int]:
    """Yield integers starting from start."""
    n = start
    while True:
        yield n
        n += 1
```

## エラーハンドリングパターン

### 具体的な例外をキャッチする

```python
from pathlib import Path


def load_config(path: Path) -> Config:
    """Load and parse a config file."""
    try:
        return Config.from_json(path.read_text())
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {path}") from e
```

### 階層的なカスタム例外

```python
class AppError(Exception):
    """Base exception for all application errors."""


class ValidationError(AppError):
    """Raised when input validation fails."""


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
```

## コンテキストマネージャー

```python
import time
from collections.abc import Generator
from contextlib import contextmanager


@contextmanager
def timer(name: str) -> Generator[None, None, None]:
    """Context manager to time a block of code."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{name} took {elapsed:.4f} seconds")
```

## 内包表記とジェネレーター

```python
# シンプルな変換にはリスト内包表記を使う
names = [user.name for user in users if user.is_active]

# 遅延評価や大きなデータセットにはジェネレーター式を使う
total = sum(x * x for x in range(1_000_000))

# ジェネレーター関数
from collections.abc import Iterator
from pathlib import Path


def read_large_file(path: Path) -> Iterator[str]:
    """Read a large file line by line."""
    with path.open() as f:
        for line in f:
            yield line.strip()
```

## データクラスと NamedTuple

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """User entity with automatic __init__, __repr__, and __eq__."""

    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
```

```python
from typing import NamedTuple


class Point(NamedTuple):
    """Immutable 2D point."""

    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        """Calculate Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
```

## デコレーター

```python
import functools
import time
from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])


def timer(func: F) -> F:
    """Decorator to time function execution."""

    @functools.wraps(func)
    def wrapper(*args: object, **kwargs: object) -> object:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result

    return wrapper  # type: ignore[return-value]
```

## アンチパターン

```python
# 悪い例: ミュータブルなデフォルト引数
def append_to(item: str, items: list[str] = []) -> list[str]: ...

# 良い例
def append_to(item: str, items: list[str] | None = None) -> list[str]:
    """Append item to the list, creating a new one if not provided."""
    if items is None:
        items = []
    items.append(item)
    return items


# 悪い例: 型チェックに type() を使う — isinstance() を使う
# 悪い例: None を == で比較する — is を使う
# 悪い例: from module import * — 明示的なインポートを使う
# 悪い例: 裸の except — 具体的な例外をキャッチする
```

## ツールの実行

```bash
uv run ruff format .
uv run ruff check . --fix
uv run pytest --cov=src --cov-report=term-missing
```
