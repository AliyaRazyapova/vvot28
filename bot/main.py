import json
from message_handler import handle_message


def handler(event, context):
    update = json.loads(event["body"])
    message = update.get("message")
    if message:
        handle_message(message, context.token["access_token"])
    return {"statusCode": 200}
