import requests
from setting_debug import Log
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append("../")
from src.api.postReplyMessage import ReplyMessage


travel_url = "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426?"
application_id = os.environ["APPLICATION_ID"]
MAX_TITLE_SIZE = 40
MAX_TEXT_SIZE = 60
MAX_ITEM_NUMBER = 10


class OverallHotel:
    def __init__(self):
        self.log = Log()
        self.latitude = 0.0
        self.longitude = 0.0
        self.reply_token = ""

    def getHotel(self, middle_class_code, small_class_code, detail_class_code):
        columns = []
        params = {
            "applicationId": application_id,
            "largeClassCode": "japan",
            "middleClassCode": middle_class_code,
            "smallClassCode": small_class_code,
            "sort": "standard",
            "hits": 30,
        }

        if detail_class_code != "NULL":
            params["detailClassCode"] = detail_class_code

        response = requests.get(travel_url, params)

        hotels = response.json()["hotels"]

        # log.showLog(hotels)
        sorted_hotels_score = sorted(
            hotels,
            key=lambda x: (
                x["hotel"][0]["hotelBasicInfo"]["reviewAverage"] is None,
                x["hotel"][0]["hotelBasicInfo"]["reviewAverage"],
            ),
            reverse=True,
        )

        items_number = 0
        for hotel in sorted_hotels_score:
            if items_number == MAX_ITEM_NUMBER:
                break

            title = hotel["hotel"][0]["hotelBasicInfo"]["hotelName"]
            text = hotel["hotel"][0]["hotelBasicInfo"]["hotelSpecial"]

            if len(title) > MAX_TITLE_SIZE:
                title = title[0:MAX_TITLE_SIZE]

            if len(text) > MAX_TEXT_SIZE:
                text = text[0:MAX_TEXT_SIZE]

            if hotel["hotel"][0]["hotelBasicInfo"]["reviewAverage"] == None:
                continue

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
            items_number = items_number + 1

        carousel_data = [
            {"type": "text", "text": "指定場所の宿です"},
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
