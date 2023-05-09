import os
import json
import requests
from time import sleep
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
CHANNEL_ID = os.getenv("CHANNEL_ID")
WARN_ONLY = os.getenv("WARN_ONLY") == "True"

class YureruyoMessage():
    def __init__(self, client, channel, response):
        
        self.message = client.chat_postMessage(text=
                                                response["Hypocenter"]["Name"] + "で地震(" +
                                                response["Hypocenter"]["Magnitude"]["String"] + ") 震度" +
                                                response["MaxIntensity"]["LongString"],
                                                channel=channel)
        self.client = client
        self.update(response)
        pass

    def update(self, response):
        self.update_blocks(response)
        self.update_attachments(response)
        self.client.chat_update(
            channel = self.message.data["channel"],
            ts = self.message.data["ts"],
            blocks = self.blocks,
            attachments = self.attachments,
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

        return self.blocks

    def update_attachments(self, response):
        self.attachments = []
        if response["Title"]["Code"] == 39:
            return
        self.attachments.append(
            {
                "color": "good" if not response.get("Warn") else "danger",
                "fields": [
                    {
                        "title": "震源地",
                        "value": response["Hypocenter"]["Name"],
                        "short": "true"
                    },
                    {
                        "title": "予想震度",
                        "value": response["MaxIntensity"]["LongString"],
                        "short": "true"
                    },
                    {
                        "title": "震源の深さ",
                        "value": response["Hypocenter"]["Location"]["Depth"]["String"],
                        "short": "true"
                    },
                    {
                        "title": "マグニチュード",
                        "value": response["Hypocenter"]["Magnitude"]["Float"],
                        "short": "true"
                    }
                ],
                "image_url": "http://my-website.com/path/to/image.jpg",
                "thumb_url": "http://example.com/path/to/thumb.png",
                "footer": "第" + str(response["Serial"]) + "報 | 気象庁発表",
                "footer_icon": "https://www.jma.go.jp/jma/kishou/img/logo2.jpg",
                "ts": response["OriginTime"]["UnixTime"]
            }
        )

    def create_postdata():
        pass

class YureruyoManager():
    def __init__(self, client, channel):
        self.messages = []
        self.client = client
        self.channel = channel
        self.update_response()
        self.original_text = self.response["OriginalText"]
        print(self.response)
        pass
    
    def update(self, response=None):
        if response == None:
            self.update_response() 
        else:
            self.response = response

        if self.original_text == self.response["OriginalText"]:
            return
        self.original_text = self.response["OriginalText"]

        if WARN_ONLY:
            if not self.response.get("Warn"):
                return
        
        print(self.response)

        for message in self.messages:
            if message["EventID"] == self.response["EventID"]:
                message["YureruyoMessage"].update(self.response)
                return
        self.messages.append(
            {
                "EventID": self.response["EventID"],
                "YureruyoMessage": YureruyoMessage(client=self.client, channel=self.channel, response=self.response)
            }
        )
    def update_response(self):
        self.response = json.loads(requests.get("https://api.iedred7584.com/eew/json/").text)

if __name__ == "__main__":

    manager = YureruyoManager(client=app.client, channel=CHANNEL_ID)
    while True:
        try:
            manager.update()
        except Exception as e:
            print("Some error occurred. Retrying in 3 seconds.")
            print(e)
            sleep(3)
            continue
        sleep(1)

