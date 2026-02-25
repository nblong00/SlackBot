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


def message_count_pull():
    raw_message_count = {}
    sql_message_counts = session.query(Message).order_by(Message.user_id).all()
    cleaned_dict = [
        dict((col, getattr(row, col)) for col in row.__table__.columns.keys())
        for row in sql_message_counts
    ]
    for entry in cleaned_dict:
        individual = entry['user_id']
        raw_message_count[individual] = entry['count']
    return raw_message_count


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    slack_user_id = event.get('user')
    text = event.get('text')
    if BOT_ID != slack_user_id:
        if slack_user_id in refined_message_count:
            refined_message_count[slack_user_id] += 1
            new_count = session.query(Message).filter(Message.user_id == slack_user_id).first()
            new_count.count = refined_message_count[slack_user_id]
            session.commit()
            print(refined_message_count)
        else:
            refined_message_count[slack_user_id] = 1
            new_count = Message(user_id = slack_user_id, count = 1)
            session.add(new_count)
            session.commit()
            print(refined_message_count)
        client.chat_postMessage(channel=channel_id, text=text)


@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = refined_message_count[user_id]
    client.chat_postMessage(channel=channel_id, text= f'Message: {message_count}')
    return Response(), 200


if __name__ == "__main__":
    refined_message_count = message_count_pull()
    print(refined_message_count) 
    app.run(debug=True)
