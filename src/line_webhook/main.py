import json


def line_webhook(request):
    event = request.get_json()
    source = event["events"][0]["source"]
    user_id = source.get("userId")
    group_id = source.get("groupId")
    print(f"Received groupId: {group_id}")  # グループIDをログ出力
    result = {"userId": user_id, "groupId": group_id}
    return (json.dumps(result), 200, {"Content-Type": "application/json"})