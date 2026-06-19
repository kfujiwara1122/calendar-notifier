import argparse
import os
from datetime import date, timedelta
from pathlib import Path

import anthropic
import requests

LINE_API_URL = "https://api.line.me/v2/bot/message/push"
PROMPT_FILE = Path(__file__).parent / "playground_prompt.md"


def get_playground_suggestion(prompt_content: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt_content}],
    )
    return message.content[0].text


def send_line_message(to: str, message: str, access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {"to": to, "messages": [{"type": "text", "text": message}]}
    response = requests.post(LINE_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Claude APIの結果を表示するだけでLINEには送信しない")
    args = parser.parse_args()

    today_date = date.today()
    today = today_date.strftime("%Y年%m月%d日")
    days_until_saturday = (5 - today_date.weekday()) % 7
    saturday = today_date + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    date_header = (
        f"今日の日付: {today}\n"
        f"今週末の日付: {saturday.strftime('%Y年%m月%d日')}（土）"
        f"〜{sunday.strftime('%Y年%m月%d日')}（日）\n\n"
    )
    prompt_content = date_header + PROMPT_FILE.read_text(encoding="utf-8")

    print("Calling Claude API for playground suggestion...")
    suggestion = get_playground_suggestion(prompt_content)
    print(f"\n--- Suggestion ---\n{suggestion}\n------------------\n")

    if args.dry_run:
        print("[DRY RUN] LINE送信をスキップしました。")
        return

    access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    line_group_id = os.environ["LINE_GROUP_ID"]

    print("Sending to LINE...")
    result = send_line_message(line_group_id, suggestion, access_token)
    print(f"LINE API response: {result}")


if __name__ == "__main__":
    main()
