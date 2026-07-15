# calendar-notifier

Google カレンダーの予定を LINE に通知する Python プロジェクト。
実行自体は GitHub Actions 上で行うが、起動トリガーは GCP Cloud Scheduler が担う。

## アーキテクチャ

```
GCP Cloud Scheduler（毎時 / 週次。Terraform で管理）
     │  HTTP POST（GitHub PAT で認証）
     ▼
GitHub REST API: POST /repos/.../dispatches（repository_dispatch イベント発火）
     ▼
GitHub Actions（repository_dispatch トリガーで起動）
     │
     ├── Google Calendar API
     └──(LINE Messaging API)──► LINE グループ
```

GitHub Actions 標準の `schedule:` (cron) トリガーはベストエフォートで、リポジトリの負荷状況等により遅延・スキップが起こりうる（実際に定期実行漏れが発生したため）。そのため「時刻になったら起動する」役割は SLA を持つ専用サービスである GCP Cloud Scheduler に持たせ、実際の処理（Google Calendar API 呼び出し・LINE 通知・Claude API 呼び出し）は従来どおり GitHub Actions 上で実行する。

- **calender_fetcher**: Cloud Scheduler から 1 時間ごとに `repository_dispatch` (`calendar-tick`) 経由で起動。Google Calendar API で直近 1 時間の予定を取得し、LINE グループに直接送信する。
- **weekly_playground_suggester**: Claude API で子供の遊び場提案文を生成し、LINE に送信するスクリプト。Cloud Scheduler から `repository_dispatch` (`playground-tick`) 経由で週次起動。
- **infra/**: 上記 Cloud Scheduler ジョブを Terraform で定義。`infra/**` を変更して `main` にマージすると `.github/workflows/infra.yml` が自動で `terraform apply` する。

## ディレクトリ構造

```
src/
  calender_fetcher/           # スクリプト: カレンダー取得 → LINE 通知
  weekly_playground_suggester/  # スクリプト: 週次遊び場提案
infra/                         # Terraform: GCP Cloud Scheduler ジョブ定義
.github/workflows/
  calendar_notifier.yml       # GitHub Actions: repository_dispatch (calendar-tick) で起動
  weekly_playground.yml       # GitHub Actions: repository_dispatch (playground-tick) で起動
  infra.yml                   # GitHub Actions: infra/ の変更を terraform plan/apply
```

## 環境変数 / シークレット

| 変数名 | 用途 | 設定場所 |
|--------|------|----------|
| `GOOGLE_CALENDAR_SERVICE_ACCOUNT` | Google サービスアカウント JSON | GitHub Secrets |
| `GOOGLE_CALENDAR_ID` | 通知対象カレンダー ID | GitHub Variables (`vars.*`) |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE アクセストークン | GitHub Secrets |
| `LINE_GROUP_ID` | 送信先 LINE グループ ID | GitHub Secrets |
| `ANTHROPIC_API_KEY` | Claude API キー | GitHub Secrets |
| `TF_VAR_github_pat` | `infra.yml` が Terraform に渡す fine-grained PAT（`repository_dispatch` 発火用） | GitHub Secrets |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `infra.yml` が GCP 認証に使う Workload Identity Federation プロバイダ | GitHub Secrets |
| `GCP_SERVICE_ACCOUNT_EMAIL` | `infra.yml` が Terraform 実行時に借用する GCP サービスアカウント | GitHub Secrets |
| `GCP_PROJECT_ID` | Cloud Scheduler ジョブを作成する GCP プロジェクト ID | GitHub Variables (`vars.*`) |
| `GCP_TFSTATE_BUCKET` | Terraform state を保存する GCS バケット名 | GitHub Variables (`vars.*`) |

### GitHub Secrets / Variables の設定

Settings → Secrets and variables → Actions で以下を登録する。

**Secrets:**
- `GOOGLE_CALENDAR_SERVICE_ACCOUNT`: サービスアカウント JSON ファイルの中身をそのまま貼り付ける
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_GROUP_ID`
- `ANTHROPIC_API_KEY`
- `TF_VAR_github_pat`: fine-grained PAT（対象リポジトリのみ・`Contents: Read and write` 権限）
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT_EMAIL`

**Variables:**
- `GOOGLE_CALENDAR_ID`: 例 `notify.fujiwara@gmail.com`
- `GCP_PROJECT_ID`
- `GCP_TFSTATE_BUCKET`

## GCP Cloud Scheduler（Terraform）の設定

`infra/` 配下の Terraform が Cloud Scheduler ジョブ（`calendar-notifier-hourly`, `weekly-playground-suggester`）を管理する。これらのジョブは GitHub の `repository_dispatch` API を叩いて上記ワークフローを起動する。運用中に頻度等を変えたい場合は `infra/main.tf` を編集して `main` にマージするだけでよく、`gcloud` コマンドを直接叩く必要はない。

### 初回のみ必要な手動セットアップ（ユーザーの GCP アカウントで実施）

1. GCP プロジェクトを用意する（以前使っていた `line-bot-419607` を流用するか新規作成）。
2. Terraform state 用の GCS バケットを作成する: `gsutil mb -l asia-northeast1 gs://<project>-tfstate`
3. Cloud Scheduler API を有効化する: `gcloud services enable cloudscheduler.googleapis.com`
4. GitHub Actions 用のサービスアカウントと Workload Identity Federation のプール/プロバイダを作成し（[google-github-actions/auth](https://github.com/google-github-actions/auth) の手順に準拠）、サービスアカウントに `roles/cloudscheduler.admin` を付与する。
5. GitHub 側で fine-grained PAT（対象リポジトリのみ・`Contents: Read and write`）を発行し、`TF_VAR_github_pat` として GitHub Secrets に登録する。
6. 上記の `GCP_WORKLOAD_IDENTITY_PROVIDER` / `GCP_SERVICE_ACCOUNT_EMAIL` / `GCP_PROJECT_ID` / `GCP_TFSTATE_BUCKET` を GitHub Secrets / Variables に登録する。

以降は `infra/**` の変更を `main` にマージすると `.github/workflows/infra.yml` が自動的に `terraform plan`（PR時）・`terraform apply`（main push時）を実行する。

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

- 環境変数は GitHub Secrets / Variables で管理する（`.env` はコミットしない）
- サービスアカウントの JSON キーはリポジトリに含めない
