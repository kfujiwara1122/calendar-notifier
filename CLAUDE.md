# calendar-notifier

Google カレンダーの予定を LINE に通知する Python プロジェクト。
Google Cloud Functions 上で動作する複数のマイクロサービスで構成されている。

## アーキテクチャ

```
calender_fetcher  ──(HTTP)──►  line_notifier  ──(LINE API)──►  LINE グループ
     │
     └── Google Calendar API
```

- **calender_fetcher**: Cloud Scheduler から 1 時間ごとに起動。Google Calendar API で直近 1 時間の予定を取得し、`line_notifier` に転送する。
- **line_notifier**: HTTP リクエストを受け取り、LINE Messaging API でグループに送信する。
- **line_webhook**: LINE からの Webhook を受け取り、グループ ID / ユーザー ID をログに記録する（初期設定用）。
- **weekly_playground_suggester**: Claude API で子供の遊び場提案文を生成し、LINE に送信するスクリプト。GitHub Actions の schedule で週次実行。

## ディレクトリ構造

```
src/
  calender_fetcher/       # Cloud Function: カレンダー取得 → LINE 通知トリガー
  line_notifier/          # Cloud Function: LINE メッセージ送信
  line_webhook/           # Cloud Function: LINE Webhook 受信
  weekly_playground_suggester/  # スクリプト: 週次遊び場提案
deploy/
  cloudbuild.yaml         # Cloud Build デプロイ設定
.github/workflows/
  deploy.yml              # GitHub Actions: main push で Cloud Build 実行
  weekly_playground.yml   # GitHub Actions: 週次スケジュール実行
```

## 環境変数

| 変数名 | 用途 | 設定場所 |
|--------|------|----------|
| `GCP_PROJECT` | GCP プロジェクト ID | Cloud Functions 環境変数 |
| `GCP_LINE_NOTIFIER_URL` | line_notifier の URL | Cloud Functions 環境変数 |
| `GOOGLE_CALENDAR_ID` | 通知対象カレンダー ID | Cloud Functions 環境変数 |
| `LINE_GROUP_ID` | 送信先 LINE グループ ID | Cloud Functions 環境変数 |
| `ANTHROPIC_API_KEY` | Claude API キー | GitHub Actions シークレット |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE アクセストークン | GitHub Actions シークレット |

シークレット（LINE トークン、GCP サービスアカウント）は GCP Secret Manager に保存し、Cloud Functions 内で取得する。

## 開発環境セットアップ

```bash
# 依存関係インストール（モジュールごと）
pip install -r src/calender_fetcher/requirements.txt
pip install -r src/line_notifier/requirements.txt
pip install -r src/weekly_playground_suggester/requirements.txt

# 開発ツール
pip install ruff mypy pytest

# コード品質チェック
ruff check src/
ruff format src/
mypy src/
```

## デプロイ

```bash
# Cloud Build 経由でデプロイ（main ブランチ push で自動実行）
gcloud builds submit --config deploy/cloudbuild.yaml .
```

## 注意事項

- `.env` ファイルはコミットしない（`.env.example` をテンプレートとして使用）
- GCP サービスアカウントの JSON キーはリポジトリに含めない
- 各 Cloud Function は `src/<module>/requirements.txt` で依存関係を個別管理している
