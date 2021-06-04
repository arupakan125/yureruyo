import requests
import json
import os
from time import sleep
from datetime import datetime, timezone, timedelta



def get_json():
    while True:
        try:
            r = requests.get("https://api.iedred7584.com/eew/json/").text
            r = json.loads(r)
        except:
            print("Some error occurred. Retrying in 3 seconds.")
            sleep(3)
            continue
        return r


def save_to_file(data):
    JST = timezone(timedelta(hours=+9), 'JST')
    target = datetime.now(JST).isoformat() + ".json"
    with open(target, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


CHANNEL_ID = os.getenv("CHANNEL_ID")
SLACK_URL = os.getenv("SLACK_URL")
r = get_json()


OriginalText = r["OriginalText"]
print(OriginalText)

sleep(1)

while True:
    sleep(1)
    r = get_json()
    if OriginalText == r["OriginalText"]:
        print("No changes")
        continue
    save_to_file(r)
    data = {
        'channel': CHANNEL_ID,
        "attachments": [
            {
                "fallback": "第" + str(r["Serial"]) + "報　" + r["Title"]["String"],
                "color": "#36a64f",
                "pretext": r["Title"]["String"],
                "fields": [
                    {
                        "title": "震源地",
                        "value": r["Hypocenter"]["Name"],
                        "short": "true"
                    },
                    {
                        "title": "予想震度",
                        "value": r["MaxIntensity"]["LongString"],
                        "short": "true"
                    },
                    {
                        "title": "震源の深さ",
                        "value": r["Hypocenter"]["Location"]["Depth"]["String"],
                        "short": "true"
                    },
                    {
                        "title": "マグニチュード",
                        "value": r["Hypocenter"]["Magnitude"]["Float"],
                        "short": "true"
                    }
                ],
                "image_url": "http://my-website.com/path/to/image.jpg",
                "thumb_url": "http://example.com/path/to/thumb.png",
                "footer": "第" + str(r["Serial"]) + "報",
                "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                "ts": r["OriginTime"]["UnixTime"]
            }
        ]
    }

    if r["Warn"]:
        data["attachments"][0]["color"] = "#ff0000"
        data["attachments"][0]["fields"].append({
            "title": "強い揺れが予想される地域",
            "value": " ".join(r["WarnForecast"]["LocalAreas"]),
        })
    OriginalText = r["OriginalText"]
    slack = requests.post(
        SLACK_URL, data=json.dumps(data))
