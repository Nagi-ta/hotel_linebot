import requests
from setting_debug import Log
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append("../")
from src.api.postReplyMessage import ReplyMessage

MAX_TITLE_SIZE = 40
MAX_TEXT_SIZE = 60
travel_url = "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426?"
# application_id = "1043478375665697187"
application_id = os.environ["APPLICATION_ID"]


class NearHotel:
    def __init__(self):
        self.latitude = 0.0
        self.longitude = 0.0
        self.reply_token = ""

    def getHotel(self, option):
        carousel_data = []
        columns = []
        params = {
            "applicationId": application_id,
            "longitude": self.longitude,
            "latitude": self.latitude,
            # 現在地周辺に宿がないときの確認用
            # "longitude": 100.0,
            # "latitude": 100.0,
            "searchRadius": 3,
            "datumType": 1,
            "sort": option,
            "hits": 10,
        }

        response = requests.get(travel_url, params)

        if "error" in response.json():
            carousel_data = [{"type": "text", "text": "現在地周辺 (3km以内) に宿がありません"}]
        else:
            hotels = response.json()["hotels"]

            for hotel in hotels:
                title = hotel["hotel"][0]["hotelBasicInfo"]["hotelName"]
                text = hotel["hotel"][0]["hotelBasicInfo"]["hotelSpecial"]
                if len(title) > MAX_TITLE_SIZE:
                    title = title[0:MAX_TITLE_SIZE]

                if len(text) > MAX_TEXT_SIZE:
                    text = text[0:MAX_TEXT_SIZE]

                columns.append(
                    {
                        "thumbnailImageUrl": hotel["hotel"][0]["hotelBasicInfo"][
                            "hotelImageUrl"
                        ],
                        "imageBackgroundColor": "#FFFFFF",
                        "title": title,
                        "text": text,
                        "defaultAction": {
                            "type": "uri",
                            "label": "ホテルの詳細",
                            "uri": hotel["hotel"][0]["hotelBasicInfo"][
                                "hotelInformationUrl"
                            ],
                        },
                        "actions": [
                            {
                                "type": "uri",
                                "label": "ホテルの詳細",
                                "uri": hotel["hotel"][0]["hotelBasicInfo"][
                                    "hotelInformationUrl"
                                ],
                            }
                        ],
                    }
                )

            carousel_data = [
                {"type": "text", "text": "現在地周辺の宿です"},
                {
                    "type": "template",
                    "altText": "carousel hotel",
                    "template": {
                        "type": "carousel",
                        "columns": columns,
                        "imageAspectRatio": "rectangle",
                        "imageSize": "cover",
                    },
                },
            ]

        reply = ReplyMessage()

        response = reply.postReply(carousel_data, self.reply_token)

        return response
