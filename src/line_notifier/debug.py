import os
from main import send_line_message
from dotenv import load_dotenv


# ローカルテスト用
if __name__ == "__main__":
    load_dotenv()
    to = os.getenv("LINE_GROUP_ID")
    message = "テストメッセージ"
    access_token_file = os.getenv("LINE_CHANNEL_ACCESS_TOKEN_FILE")
    if not access_token_file:
        print("環境変数 LINE_CHANNEL_ACCESS_TOKEN_FILE が設定されていません")
        exit(1)
    try:
        with open(access_token_file, "r", encoding="utf-8") as f:
            access_token = f.read().strip()
        result = send_line_message(to, message, access_token)
        print("送信成功:", result)
    except Exception as e:
        print("送信失敗:", e)