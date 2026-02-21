from slack_sdk import WebClient
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import os

load_dotenv()
app = Flask(__name__)
client = WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call('auth.test')['user_id']
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)

message_counts = {}


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else: 
            message_counts[user_id] = 1
        client.chat_postMessage(channel=channel_id, text=text)


@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = message_counts.get(user_id, 0)
    client.chat_postMessage(channel=channel_id, text= f'Message: {message_count}')
    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
