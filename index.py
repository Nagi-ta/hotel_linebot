# Python 3.10.4
# Flask 2.1.2
# Flaskの公式ドキュメント：https://flask.palletsprojects.com/en/2.1.x/
# python3の公式ドキュメント：https://docs.python.org/ja/3.10/
# python3の基礎文法のわかりやすいサイト：https://note.nkmk.me/python/
# 使用するモジュールのインポート
# pythonが提供しているモジュールのインポート

from email.base64mime import body_encode
import json
from pydoc import locate
from flask import Flask, request, jsonify
from src.api.postReplyMessage import ReplyMessage

# 自分で作成したモジュールのインポート
from database import Database
from setting_debug import Log
from src.position.getCurrentPosition import Position
from src.hotel.getNearHotel import NearHotel
from src.hotel.getSelectedHotel import OverallHotel
from src.hotel.postLocationOption import Hotel

# Flaskクラスをnewしてappに代入
# gunicornの起動コマンドに使用しているのでここは変更しないこと
app = Flask(__name__)

# 「/」にPOSTリクエストが来た場合、index関数が実行される
@app.route("/", methods=["POST"])
def index():
    log = Log()

    # POSTリクエストのbodyを取得
    body_binary = request.get_data()
    body = json.loads(body_binary.decode())
    # log.showLog(body)

    events_body = body["events"][0]
    reply_token = events_body["replyToken"]

    if events_body["type"] == "follow":
        reply = ReplyMessage()
        messages = [
            {"type": "text", "text": "お友達追加ありがとうございます！"},
            {"type": "text", "text": "下のメニューから操作してください！"},
        ]
        response = reply.postReply(messages, reply_token)
        # log.showLog(response)

    else:
        message_type = events_body["message"]["type"]
        userId = events_body["source"]["userId"]
        if message_type == "location":
            db = Database()
            near_hotel = NearHotel()
            near_hotel.latitude = events_body["message"]["latitude"]
            near_hotel.longitude = events_body["message"]["longitude"]
            near_hotel.reply_token = reply_token
            locate_option = db.getLocateOption(userId)
            response = near_hotel.getHotel(locate_option)
            # log.showLog(response)

        elif message_type == "text":
            db = Database()
            hotel = Hotel()
            hotel.reply_token = reply_token
            message_text = events_body["message"]["text"]

            if message_text == "現在地に近いホテルを検索":
                db.checkUserId(userId)
                position = Position()
                position.reply_token = reply_token
                response = position.getOption()
                # log.showLog(response)

            elif (
                message_text == "距離が近い順"
                or message_text == "値段が安い順"
                or message_text == "値段が高い順"
            ):
                position = Position()
                position.reply_token = reply_token
                locate_option = ""

                if message_text == "距離が近い順":
                    locate_option = db.updateLocateOption(userId, "standard")
                elif message_text == "値段が安い順":
                    locate_option = db.updateLocateOption(userId, "+roomCharge")
                elif message_text == "値段が高い順":
                    locate_option = db.updateLocateOption(userId, "-roomCharge")
                response = position.getPosition()

            elif message_text == "都道府県を指定して検索":
                db.checkUserId(userId)
                response = hotel.selectRegion()
                # log.showLog(response)

            elif db.checkDetail(userId, message_text):
                prefecture, city, detail = db.getPrefecturesParams(userId)
                overall_hotel = OverallHotel()
                overall_hotel.reply_token = reply_token
                response = overall_hotel.getHotel(prefecture, city, detail)
                # log.showLog(response)

            elif message_text == "次の詳細候補":
                detail = db.updateDetailState(userId, 1)
                detailList = db.getDetail(userId, detail)
                response = hotel.selectDetail(detailList, 12)
                # log.showLog(response)

            elif message_text == "前の詳細候補":
                detail = db.updateDetailState(userId, 0)
                log.showLog(detail)
                detailList = db.getDetail(userId, detail)
                log.showLog(detail)
                response = hotel.selectDetail(detailList, 0)
                # log.showLog(response)

            elif db.checkCity(userId, message_text):
                detail_list = db.getDetail(userId, message_text)
                if len(detail_list) == 0:
                    prefecture, city, detail = db.getPrefecturesParams(userId)
                    overall_hotel = OverallHotel()
                    overall_hotel.reply_token = reply_token
                    response = overall_hotel.getHotel(prefecture, city, detail)
                    # log.showLog(response)
                else:
                    response = hotel.selectDetail(detail_list, 0)
                    # log.showLog(response)

            elif message_text == "次の市町村候補":
                prefecture = db.updateCityState(userId, 1)
                cityList = db.getCity(userId, prefecture)
                response = hotel.selectCity(cityList, 12)
                # log.showLog(response)

            elif message_text == "前の市町村候補":
                prefecture = db.updateCityState(userId, 0)
                cityList = db.getCity(userId, prefecture)
                response = hotel.selectCity(cityList, 0)
                # log.showLog(response)

            elif db.checkPrefecture(userId, message_text):
                cityList = db.getCity(userId, message_text)
                response = hotel.selectCity(cityList, 0)
                # log.showLog(response)

            elif db.checkResion(userId, message_text):
                prefectureList = db.getPrefecture(userId)
                response = hotel.selectPrefecture(prefectureList)
                # log.showLog(response)

            else:
                reply = ReplyMessage()
                messages = [{"type": "text", "text": "ボタンで操作してください"}]
                response = reply.postReply(messages, reply_token)
                # log.showLog(response)

    return jsonify({"message": "OK"}), 200
