import os
import json
from main import fetch_events
from dotenv import load_dotenv

# ローカルテスト用
if __name__ == "__main__":
    load_dotenv()
    gcp_service_account_info_file = os.getenv("GCP_SERVICE_ACCOUNT_INFO_FILE")
    if not gcp_service_account_info_file:
        print("環境変数 GCP_SERVICE_ACCOUNT_INFO_FILE が設定されていません")
        exit(1)
    try:
        with open(gcp_service_account_info_file, "r", encoding="utf-8") as f:
            service_account_info = json.load(f)
        events = fetch_events(service_account_info)
        print("取得した予定:")
        print(json.dumps(events, ensure_ascii=False, indent=2))
    except Exception as e:
        print("取得失敗:", e)
