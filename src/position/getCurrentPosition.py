import sys

sys.path.append("../")
from src.api.postReplyMessage import ReplyMessage


class Position:
    def __init__(self):
        self.reply_token = ""
        self.reply_message = ReplyMessage()

    def getOption(self):
        data = [
            {
                "type": "text",
                "text": "オプションを選択してください",
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "距離が近い順",
                                "text": "距離が近い順",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "値段が安い順",
                                "text": "値段が安い順",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "値段が高い順",
                                "text": "値段が高い順",
                            },
                        },
                    ]
                },
            }
        ]
        response = self.reply_message.postReply(data, self.reply_token)

        return response

    def getPosition(self):
        data = [
            {
                "type": "text",
                "text": "現在地を送ってください",
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "action": {"type": "location", "label": "現在地を送る"},
                        }
                    ]
                },
            }
        ]
        response = self.reply_message.postReply(data, self.reply_token)

        return response
