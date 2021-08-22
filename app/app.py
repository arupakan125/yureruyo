import os
import json
import requests
from time import sleep
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
CHANNEL_ID = os.getenv("CHANNEL_ID")

class YureruyoMessage():
    def __init__(self, client, channel, response):
        
        self.message = client.chat_postMessage(text="緊急地震速報を受信しました。", channel=channel)
        self.client = client
        self.update(response)
        pass

    def update(self, response):
        self.update_blocks(response)
        self.client.chat_update(
            channel = self.message.data["channel"],
            ts = self.message.data["ts"],
            blocks = self.blocks,
            text = "緊急地震速報を受信しました。",
        )

    def update_blocks(self, response):
        self.blocks = []
        if response["Title"]["Code"] != 39:
            self.blocks.append(
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": response["Title"]["String"],
                        "emoji": True
                    }
                }
            )
            if response.get("Warn"):
                self.blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*強い揺れが予想される地域*\n" + " ".join(response["WarnForecast"]["LocalAreas"])
                        }
                    }
                )
            else:
                self.blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*この情報は誤差を含む可能性があります*"
                        }
                    }
                )
        else:
            self.blocks.append(
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "緊急地震速報はキャンセルされました",
                        "emoji": True
                    }
                }
            )

        if response.get("Hypocenter"):
            self.blocks.append(
                {
                    "type": "divider"
                }
            )
            self.blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*発生日時*\n" + response["OriginTime"]["String"]
                    },
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*震源地*\n" + response["Hypocenter"]["Name"],
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*予想震度*\n" + response["MaxIntensity"]["LongString"],
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*震源の深さ*\n" + response["Hypocenter"]["Location"]["Depth"]["String"]
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*マグニチュード*\n" + str(response["Hypocenter"]["Magnitude"]["Float"])
                        }
                    ]
                }
            )
        self.blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "image",
                        "image_url": "https://www.jma.go.jp/jma/kishou/img/logo2.jpg",
                        "alt_text": "JMA Logo"
                    },
                    {
                        "type": "plain_text",
                        "text": "第" + str(response["Serial"]) + "報 | 気象庁発表",
                        "emoji": True
                    }
                ]
            }
        )
        self.blocks.append(
            {
                "type": "divider"
            }
        )
        return self.blocks

    def create_postdata():
        pass

class YureruyoManager():
    def __init__(self, client, channel, response):
        self.messages = []
        self.client = client
        self.channel = channel
        self.response = response
        self.original_text = response["OriginalText"]
        print(response)
        pass
    
    def update(self, response):
        if self.original_text == response["OriginalText"]:
            return
        self.original_text = response["OriginalText"]
        print(response)

        for message in self.messages:
            if message["EventID"] == response["EventID"]:
                message["YureruyoMessage"].update(response)
                return
        self.messages.append(
            {
                "EventID": response["EventID"],
                "YureruyoMessage": YureruyoMessage(client=self.client, channel=self.channel, response=response)
            }
        )

if __name__ == "__main__":
    response = json.loads(requests.get("https://api.iedred7584.com/eew/json/").text)

    manager = YureruyoManager(client=app.client, channel=CHANNEL_ID, response=response)
    while True:
        try:
            response = json.loads(requests.get("https://api.iedred7584.com/eew/json/").text)
            manager.update(response)
        except:
            print("Some error occurred. Retrying in 3 seconds.")
            sleep(3)
            continue
        sleep(1)

