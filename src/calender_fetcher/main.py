import os
import datetime
import json
import sys
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account

LINE_API_URL = "https://api.line.me/v2/bot/message/push"


def get_hour_range(dt=None):
    if dt is None:
        dt = datetime.datetime.utcnow()
    start = dt.replace(minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(minutes=59, seconds=59)
    return start.isoformat() + "Z", end.isoformat() + "Z"


def fetch_events():
    service_account_info = json.loads(os.environ["GOOGLE_CALENDAR_SERVICE_ACCOUNT"])
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    )
    service = build("calendar", "v3", credentials=credentials)
    calendar_id = os.environ["GOOGLE_CALENDAR_ID"]
    time_min, time_max = get_hour_range()
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])


def create_event_message(event):
    parts = [event["summary"]]
    if "description" in event:
        parts.append("----")
        parts.append(event["description"])
    return "\n".join(parts)


def send_line_message(to, message):
    headers = {
        "Authorization": f"Bearer {os.environ['LINE_CHANNEL_ACCESS_TOKEN']}",
        "Content-Type": "application/json",
    }
    payload = {"to": to, "messages": [{"type": "text", "text": message}]}
    response = requests.post(LINE_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def main():
    events = fetch_events()
    line_group_id = os.environ["LINE_GROUP_ID"]
    failed = False
    for event in events:
        message = create_event_message(event)
        try:
            send_line_message(line_group_id, message)
            print(f"送信成功: {event.get('summary', '')}")
        except Exception as e:
            print(f"送信失敗: {event.get('summary', '')}, error={e}", file=sys.stderr)
            failed = True
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
