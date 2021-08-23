import os
import json
import requests
from app import YureruyoManager
from slack_bolt import App
from time import sleep

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
CHANNEL_ID = os.getenv("CHANNEL_ID")


manager = YureruyoManager(client=app.client, channel=CHANNEL_ID)

json_open = open('./sample/1.json', 'r')
response = json.load(json_open)
manager.update(response)
sleep(2)

json_open = open('./sample/2.json', 'r')
response = json.load(json_open)
manager.update(response)
sleep(2)

json_open = open('./sample/3.json', 'r')
response = json.load(json_open)
manager.update(response)
sleep(2)