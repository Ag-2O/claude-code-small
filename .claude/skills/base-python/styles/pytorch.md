# PyTorch パターン集

## 基本原則

### 1. デバイス非依存なコード

デバイスをハードコードせず、CPU でも GPU でも動くコードを書く。

```python
# 良い例: デバイス非依存
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MyModel().to(device)
data = data.to(device)

# 悪い例: デバイスをハードコード
model = MyModel().cuda()  # GPU がない環境でクラッシュする
data = data.cuda()
```

### 2. 再現性

すべての乱数シードを設定して、結果を再現できるようにする。

```python
# 良い例: 完全な再現性セットアップ
def set_seed(seed: int = 42) -> None:
    """Set all random seeds for reproducible experiments."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# 悪い例: シードを設定しない
model = MyModel()  # 実行のたびに重みが変わる
```

### 3. テンソルのシェイプをアノテーションする

コメントでテンソルのシェイプを常にドキュメント化・確認する。

```python
# 良い例: シェイプのアノテーション付き forward
def forward(self, x: torch.Tensor) -> torch.Tensor:
    # x: (batch_size, channels, height, width)
    x = self.conv1(x)        # -> (batch_size, 32, H, W)
    x = self.pool(x)         # -> (batch_size, 32, H//2, W//2)
    x = x.view(x.size(0), -1)  # -> (batch_size, 32*H//2*W//2)
    return self.fc(x)        # -> (batch_size, num_classes)

# 悪い例: シェイプを追跡しない
def forward(self, x):
    x = self.conv1(x)
    x = self.pool(x)
    x = x.view(x.size(0), -1)  # このサイズは何？
    return self.fc(x)           # 動くかどうか不明
```

## モデルアーキテクチャパターン

### nn.Module の基本構造

```python
# 良い例: 整理された nn.Module
class ImageClassifier(nn.Module):
    """Simple CNN image classifier."""

    def __init__(self, num_classes: int, dropout: float = 0.5) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(64 * 16 * 16, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)

# 悪い例: すべてを forward 内に書く
class ImageClassifier(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        x = F.conv2d(x, weight=self.make_weight())  # 毎回呼び出すたびに重みを再生成する
        return x
```

### 重みの初期化

```python
# 良い例: 明示的な初期化
def _init_weights(self, module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Conv2d):
        nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
    elif isinstance(module, nn.BatchNorm2d):
        nn.init.ones_(module.weight)
        nn.init.zeros_(module.bias)

model = MyModel()
model.apply(model._init_weights)
```

## トレーニングループパターン

### 標準的なトレーニングループ

```python
# 良い例: ベストプラクティスを含む完全なトレーニングループ
def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    scaler: torch.amp.GradScaler | None = None,
) -> float:
    """Train the model for one epoch and return the average loss."""
    model.train()  # 常にトレーニングモードを設定する
    total_loss = 0.0

    for batch_idx, (data, target) in enumerate(dataloader):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad(set_to_none=True)  # zero_grad() より効率的

        # 混合精度トレーニング
        with torch.amp.autocast("cuda", enabled=scaler is not None):
            output = model(data)
            loss = criterion(output, target)

        if scaler is not None:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)
```

### 検証ループ

```python
# 良い例: 正しい評価処理
@torch.no_grad()  # コンテキストマネージャーでラップするより効率的
def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    """Evaluate the model and return the average loss and accuracy."""
    model.eval()  # 常に eval モードを設定する（Dropout を無効化し、BatchNorm に running stats を使わせる）
    total_loss = 0.0
    correct = 0
    total = 0

    for data, target in dataloader:
        data, target = data.to(device), target.to(device)
        output = model(data)
        total_loss += criterion(output, target).item()
        correct += (output.argmax(1) == target).sum().item()
        total += target.size(0)

    return total_loss / len(dataloader), correct / total
```

## データパイプラインパターン

### カスタムデータセット

```python
# 良い例: 型ヒント付きのクリーンな Dataset
class ImageDataset(Dataset):
    """Dataset that loads images from a directory with their labels."""

    def __init__(
        self,
        image_dir: str,
        labels: dict[str, int],
        transform: transforms.Compose | None = None,
    ) -> None:
        self.image_paths = list(Path(image_dir).glob("*.jpg"))
        self.labels = labels
        self.transform = transform

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        img = Image.open(self.image_paths[idx]).convert("RGB")
        label = self.labels[self.image_paths[idx].stem]

        if self.transform:
            img = self.transform(img)

        return img, label
```

### DataLoader の設定

```python
# 良い例: 最適化された DataLoader
dataloader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,             # トレーニング時はシャッフルする
    num_workers=4,            # データを並列ロードする
    pin_memory=True,          # CPU から GPU への転送を高速化する
    persistent_workers=True,  # エポック間でワーカーを維持する
    drop_last=True,           # BatchNorm のためにバッチサイズを一定に保つ
)

# 悪い例: デフォルト設定では遅い
dataloader = DataLoader(dataset, batch_size=32)  # num_workers=0、pin_memory なし
```

### collate_fn を使った可変長データ

```python
# 良い例: collate_fn でシーケンスをパディングする
def collate_fn(batch: list[tuple[torch.Tensor, int]]) -> tuple[torch.Tensor, torch.Tensor]:
    """Pad variable-length sequences in a batch to the same length."""
    sequences, labels = zip(*batch)
    # バッチ内で最も長いシーケンスに合わせてパディングする
    padded = nn.utils.rnn.pad_sequence(sequences, batch_first=True, padding_value=0)
    return padded, torch.tensor(labels)

dataloader = DataLoader(dataset, batch_size=32, collate_fn=collate_fn)
```

## チェックポイントパターン

### チェックポイントの保存と読み込み

```python
# 良い例: トレーニング状態をすべて含む完全なチェックポイント
def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    loss: float,
    path: str,
) -> None:
    """Save the full training state (model, optimizer, epoch, loss) to a file."""
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "loss": loss,
        },
        path,
    )


def load_checkpoint(
    path: str,
    model: nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
) -> dict:
    """Load a checkpoint into the model (and optimizer) and return its contents."""
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    if optimizer:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    return checkpoint

# 悪い例: 重みだけ保存する（トレーニングを再開できない）
torch.save(model.state_dict(), "model.pt")
```

## パフォーマンス最適化

### 混合精度トレーニング（AMP）

```python
# 良い例: GradScaler を使った AMP
scaler = torch.amp.GradScaler("cuda")
for data, target in dataloader:
    with torch.amp.autocast("cuda"):
        output = model(data)
        loss = criterion(output, target)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
    optimizer.zero_grad(set_to_none=True)
```

### 大規模モデルの勾配チェックポイント

```python
# 良い例: 逆伝播時に活性化を再計算してメモリを節約する
from torch.utils.checkpoint import checkpoint


class LargeModel(nn.Module):
    """Large model that uses gradient checkpointing to save memory."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 逆伝播時に活性化を再計算してメモリ使用量を削減する
        x = checkpoint(self.block1, x, use_reentrant=False)
        x = checkpoint(self.block2, x, use_reentrant=False)
        return self.head(x)
```

### torch.compile による高速化

```python
# 良い例: コンパイルでモデルを高速化する（PyTorch 2.0+）
model = MyModel().to(device)
model = torch.compile(model, mode="reduce-overhead")

# mode: "default"（安全）、"reduce-overhead"（高速）、"max-autotune"（最速）
```

## アンチパターン

```python
# 悪い例: 検証時に model.eval() を忘れる
model.train()
with torch.no_grad():
    output = model(val_data)  # Dropout がまだ有効！BatchNorm がバッチ統計を使う！

# 良い例: 検証前に eval モードを設定する
model.eval()
with torch.no_grad():
    output = model(val_data)

# 悪い例: インプレース演算で autograd を壊す
x = F.relu(x, inplace=True)  # 勾配計算が破壊される可能性がある
x += residual                  # インプレース加算で autograd グラフが壊れる

# 良い例: アウトオブプレース演算を使う
x = F.relu(x)
x = x + residual

# 悪い例: トレーニングループ内でモデルを移動する
for data, target in dataloader:
    model = model.cuda()  # 毎イテレーションでモデルを移動する！

# 良い例: ループ前に 1 回だけ移動する
model = model.to(device)
for data, target in dataloader:
    data, target = data.to(device), target.to(device)

# 悪い例: backward の前に .item() を呼ぶ
loss = criterion(output, target).item()  # 計算グラフから切り離される！
loss.backward()  # エラー: .item() 後は逆伝播できない

# 良い例: ログ記録のために backward の後に .item() を呼ぶ
loss = criterion(output, target)
loss.backward()
print(f"Loss: {loss.item():.4f}")  # backward の後は安全

# 悪い例: モデル全体を保存する（移植性が低く、壊れやすい）
torch.save(model, "model.pt")

# 良い例: state_dict を保存する
torch.save(model.state_dict(), "model.pt")
```

## クイックリファレンス

| イディオム                              | 説明                                             |
| --------------------------------------- | ------------------------------------------------ |
| `model.train()` / `model.eval()`        | トレーニング・評価の前に必ずモードを設定する     |
| `torch.no_grad()`                       | 推論時に勾配計算を無効化する                     |
| `optimizer.zero_grad(set_to_none=True)` | より効率的な勾配のクリア                         |
| `.to(device)`                           | デバイス非依存な方法でテンソルとモデルを配置する |
| `torch.amp.autocast`                    | 混合精度で約 2 倍の高速化                        |
| `pin_memory=True`                       | CPU から GPU へのデータ転送を高速化する          |
| `torch.compile`                         | JIT コンパイルで高速化する（2.0+）               |
| `weights_only=True`                     | 安全なモデルの読み込み                           |
| `torch.manual_seed`                     | 再現性のある実験                                 |
| `gradient_checkpointing`                | 計算とメモリを交換して節約する                   |
