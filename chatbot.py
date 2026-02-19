from slack_sdk import WebClient
from dotenv import load_dotenv
import os

load_dotenv()
client = WebClient(token=os.environ['SLACK_TOKEN'])
client.chat_postMessage(channel='test-bot', text='Hello world!')
