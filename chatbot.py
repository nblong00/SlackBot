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

welcome_messages = {}

class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to the test channel! \n\n'
                '*Please complete the tasks!*'
            )
        }
    }

    DIVIDER = {'type': 'divider'}

    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False
    
    def get_message (self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': '/WelcomeRobot/',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'
        text = f'{checkmark} *React to this message!*'
        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}


def send_welcome_message(channel, user):
    welcome = WelcomeMessage(channel, user)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']
    if channel not in welcome_messages:
        welcome_messages[channel] = {}
    welcome_messages[channel][user] = welcome
    print(welcome_messages[channel][user].timestamp)


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    slack_user_id = event.get('user')
    text = event.get('text')
    current_count = session.query(Message).filter(Message.user_id == slack_user_id).first()
    if slack_user_id != None and BOT_ID != slack_user_id:
        if current_count != None:
            current_count.count += 1
        else:
            new_db_entry = Message(user_id = slack_user_id, count = 1)
            session.add(new_db_entry)
        session.commit()
        client.chat_postMessage(channel=channel_id, text=text)
        if text.lower() == 'welcome':
            send_welcome_message(f'@{slack_user_id}', slack_user_id)


@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    slack_user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = session.query(Message).filter(Message.user_id == slack_user_id).first()
    client.chat_postMessage(channel=channel_id, text= f'Message: {message_count.count}')
    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
