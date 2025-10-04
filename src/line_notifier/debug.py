import os
from main import send_line_message
from dotenv import load_dotenv


# ローカルテスト用
if __name__ == "__main__":
    load_dotenv()
    to = os.getenv("GROUP_ID")
    message = "テストメッセージ"
    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    try:
        result = send_line_message(to, message, access_token)
        print("送信成功:", result)
    except Exception as e:
        print("送信失敗:", e)