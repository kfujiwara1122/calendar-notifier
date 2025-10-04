import os
import requests
from google.cloud import secretmanager


LINE_API_URL = "https://api.line.me/v2/bot/message/push"


def get_line_channel_access_token():
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv("GCP_PROJECT")  # Cloud Functions環境変数から取得
    secret_id = "LINE_CHANNEL_ACCESS_TOKEN"
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def send_line_message(to, message, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {"to": to, "messages": [{"type": "text", "text": message}]}
    response = requests.post(LINE_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def main(request):
    data = request.get_json()
    to = data.get("to")
    message = data.get("message")
    if not to or not message:
        return "Missing 'to' or 'message'", 400
    access_token = get_line_channel_access_token()
    if not access_token:
        raise ValueError("LINE_CHANNEL_ACCESS_TOKENが取得できません")
    result = send_line_message(to, message, access_token)
    return str(result), 200
