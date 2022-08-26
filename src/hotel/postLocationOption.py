from setting_debug import Log
import sys

sys.path.append("../")
from src.api.postReplyMessage import ReplyMessage

ITEMS_MAX = 13


class Hotel:
    def __init__(self):
        self.log = Log()
        self.reply_token = ""
        self.reply_message = ReplyMessage()

    def selectRegion(self):
        data = [
            {
                "type": "text",
                "text": "地方を選択してください",
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "北海道・東北",
                                "text": "北海道・東北",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "関東",
                                "text": "関東",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "中部",
                                "text": "中部",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "近畿",
                                "text": "近畿",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "中国・四国",
                                "text": "中国・四国",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "九州・沖縄",
                                "text": "九州・沖縄",
                            },
                        },
                    ]
                },
            }
        ]
        response = self.reply_message.postReply(data, self.reply_token)
        return response

    def selectPrefecture(self, datas):
        items = []

        for prefecture in datas:
            data = {
                "type": "action",
                "action": {
                    "type": "message",
                    "label": prefecture["middle_class_name"],
                    "text": prefecture["middle_class_name"],
                },
            }
            items.append(data)

        data = [
            {"type": "text", "text": "都道府県を選択してください", "quickReply": {"items": items}}
        ]
        response = self.reply_message.postReply(data, self.reply_token)
        return response

    def selectCity(self, datas, start_position):
        items = []
        i = 0
        j = 0

        for city in datas:
            if j < start_position:
                j = j + 1
                continue

            if i == ITEMS_MAX:
                break

            if i == ITEMS_MAX - 1:
                data = {
                    "type": "action",
                    "action": {
                        "type": "message",
                        "label": "次の市町村候補",
                        "text": "次の市町村候補",
                    },
                }
            else:
                data = {
                    "type": "action",
                    "action": {
                        "type": "message",
                        "label": city["small_class_name"],
                        "text": city["small_class_name"],
                    },
                }
            items.append(data)
            i = i + 1

        if j > 0:
            data = {
                "type": "action",
                "action": {
                    "type": "message",
                    "label": "前の市町村候補",
                    "text": "前の市町村候補",
                },
            }
            items.append(data)

        data = [
            {"type": "text", "text": "市町村を選択してください", "quickReply": {"items": items}}
        ]
        response = self.reply_message.postReply(data, self.reply_token)
        return response

    def selectDetail(self, datas, start_position):
        items = []
        i = 0
        j = 0

        for detail in datas:
            if j < start_position:
                j = j + 1
                continue

            if i == ITEMS_MAX:
                break

            if i == ITEMS_MAX - 1:
                data = {
                    "type": "action",
                    "action": {
                        "type": "message",
                        "label": "次の詳細候補",
                        "text": "次の詳細候補",
                    },
                }
            else:
                data = {
                    "type": "action",
                    "action": {
                        "type": "message",
                        "label": detail["detail_class_name"],
                        "text": detail["detail_class_name"],
                    },
                }
            items.append(data)
            i = i + 1

        if j > 0:
            data = {
                "type": "action",
                "action": {
                    "type": "message",
                    "label": "前の詳細候補",
                    "text": "前の詳細候補",
                },
            }
            items.append(data)

        data = [{"type": "text", "text": "詳細を選択してください", "quickReply": {"items": items}}]
        response = self.reply_message.postReply(data, self.reply_token)
        return response
