import requests
import json


class ReplyMessage:
    def postReply(self, messages, reply_token):
        payload = {
            "replyToken": reply_token,
            "messages": messages,
        }
        response = requests.post(
            url="https://api.line.me/v2/bot/message/reply",
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {gceimIykTEJoCSKaqmxnBQHsC5gnushe5dyYT/licn26bu5oFKywOr5sLPECszF+kVdLwgIt0AeP9VMzuw8OcUFUtxDVSVPDAOjYrGrssEnGBTJJ95TOzYrFL8WONaGhFkQ22ZY8GV+WtJ7wlPvKLAdB04t89/1O/w1cDnyilFU=}",
            },
        )

        return response.json()
