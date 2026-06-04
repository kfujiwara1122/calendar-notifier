# calendar-notifier

Google カレンダーの予定を LINE に通知する Python プロジェクト。
GitHub Actions のスケジュール実行で動作する。

## アーキテクチャ

```
GitHub Actions (毎時)
     │
     ├── Google Calendar API
     └──(LINE Messaging API)──► LINE グループ
```

- **calender_fetcher**: GitHub Actions から 1 時間ごとに起動。Google Calendar API で直近 1 時間の予定を取得し、LINE グループに直接送信する。
- **weekly_playground_suggester**: Claude API で子供の遊び場提案文を生成し、LINE に送信するスクリプト。GitHub Actions の schedule で週次実行。

## ディレクトリ構造

```
src/
  calender_fetcher/           # スクリプト: カレンダー取得 → LINE 通知
  weekly_playground_suggester/  # スクリプト: 週次遊び場提案
.github/workflows/
  calendar_notifier.yml       # GitHub Actions: 毎時スケジュール実行
  weekly_playground.yml       # GitHub Actions: 週次スケジュール実行
```

## 環境変数 / シークレット

| 変数名 | 用途 | 設定場所 |
|--------|------|----------|
| `GOOGLE_CALENDAR_SERVICE_ACCOUNT` | Google サービスアカウント JSON | GitHub Secrets |
| `GOOGLE_CALENDAR_ID` | 通知対象カレンダー ID | GitHub Variables (`vars.*`) |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE アクセストークン | GitHub Secrets |
| `LINE_GROUP_ID` | 送信先 LINE グループ ID | GitHub Secrets |
| `ANTHROPIC_API_KEY` | Claude API キー | GitHub Secrets |

### GitHub Secrets / Variables の設定

Settings → Secrets and variables → Actions で以下を登録する。

**Secrets:**
- `GOOGLE_CALENDAR_SERVICE_ACCOUNT`: サービスアカウント JSON ファイルの中身をそのまま貼り付ける
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_GROUP_ID`
- `ANTHROPIC_API_KEY`

**Variables:**
- `GOOGLE_CALENDAR_ID`: 例 `notify.fujiwara@gmail.com`

## 開発環境セットアップ

```bash
# 依存関係インストール
pip install -r src/calender_fetcher/requirements.txt
pip install -r src/weekly_playground_suggester/requirements.txt

# 開発ツール
pip install ruff mypy pytest

# コード品質チェック
ruff check src/
ruff format src/
mypy src/
```

## 注意事項

- `.env` ファイルはコミットしない（`.env.example` をテンプレートとして使用）
- サービスアカウントの JSON キーはリポジトリに含めない
