import os
import sys
from pathlib import Path

import anthropic
import requests

LINE_API_URL = "https://api.line.me/v2/bot/message/push"
PROMPT_FILE = Path(__file__).parent.parent.parent / "playground_prompt.md"


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
    prompt_content = PROMPT_FILE.read_text(encoding="utf-8")

    print("Calling Claude API for playground suggestion...")
    suggestion = get_playground_suggestion(prompt_content)
    print(f"Suggestion:\n{suggestion}")

    access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    line_group_id = os.environ["LINE_GROUP_ID"]

    print("Sending to LINE...")
    result = send_line_message(line_group_id, suggestion, access_token)
    print(f"LINE API response: {result}")


if __name__ == "__main__":
    main()
