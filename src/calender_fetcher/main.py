import os
import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.cloud import secretmanager
import requests
import json
import google.auth
import google.auth.transport.requests
import google.oauth2.id_token


def get_service_account_info():
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv("GCP_PROJECT")
    secret_id = "GOOGLE_CALENDAR_SERVICE_ACCOUNT"
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def get_hour_range(dt=None):
    if dt is None:
        dt = datetime.datetime.utcnow()
    start = dt.replace(minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(minutes=59, seconds=59)
    return start.isoformat() + "Z", end.isoformat() + "Z"


def fetch_events(service_account_info=None):
    if service_account_info is None:
        service_account_info = get_service_account_info()
    if isinstance(service_account_info, str):
        import json

        service_account_info = json.loads(service_account_info)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    )
    service = build("calendar", "v3", credentials=credentials)
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
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
    events = events_result.get("items", [])
    return events


def create_event_message(event):
    message = [event["summary"]]
    if "description" in event:
        message.append("----")
        message.append(event["description"])
    return "\n".join(message)


def get_id_token(target_url):
    credentials, _ = google.auth.default()
    request = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(request, target_url)
    return id_token


def main(request):
    events = fetch_events()
    LINE_API_URL = os.getenv("GCP_LINE_NOTIFIER_URL")
    LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")
    results = []
    id_token = get_id_token(LINE_API_URL)
    headers = {"Authorization": f"Bearer {id_token}"}
    for event in events:
        message = create_event_message(event)
        data = {"to": LINE_GROUP_ID, "message": message}
        try:
            response = requests.post(LINE_API_URL, json=data, headers=headers)
            if response.status_code == 200:
                print(f"送信成功: {message}")
                results.append({"event": event.get("summary", ""), "status": "success"})
            else:
                print(
                    f"送信失敗: {message}, status_code={response.status_code}, response={response.text}"
                )
                results.append(
                    {
                        "event": event.get("summary", ""),
                        "status": "failed",
                        "error": response.text,
                    }
                )
        except Exception as e:
            print(f"送信例外: {message}, error={e}")
            results.append(
                {"event": event.get("summary", ""), "status": "error", "error": str(e)}
            )
    result_json = json.dumps(
        {"count": len(results), "results": results}, ensure_ascii=False
    )
    return result_json, 200, {"Content-Type": "application/json"}
