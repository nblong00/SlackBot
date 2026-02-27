from slack_sdk import WebClient
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from models import session, Message
import os

load_dotenv()
app = Flask(__name__)
client = WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call('auth.test')['user_id']
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    slack_user_id = event.get('user')
    text = event.get('text')
    current_count = session.query(Message).filter(Message.user_id == slack_user_id).first()
    if BOT_ID != slack_user_id:
        if current_count != None:
            current_count.count += 1
        else:
            new_db_entry = Message(user_id = slack_user_id, count = 1)
            session.add(new_db_entry)
        session.commit()
        client.chat_postMessage(channel=channel_id, text=text)


@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    # message_count = refined_message_count[user_id]
    client.chat_postMessage(channel=channel_id, text= f'Message: {message_count}')
    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
