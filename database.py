from cgitb import handler
from multiprocessing.util import get_logger
from stat import filemode
import pymysql  # 参考: https://pymysql.readthedocs.io/en/latest/index.html
import pymysql.cursors
import logging
from setting_debug import Log
from src.api.getLocationCode import LocationCode

# ログの設定
format = "%(asctime)s: %(levelname)s: %(pathname)s: line %(lineno)s: %(message)s"
logging.basicConfig(
    filename="/var/log/intern2/flask.log",
    level=logging.DEBUG,
    format=format,
    datefmt="%Y-%m-%d %H:%M:%S",
)

connection = pymysql.connect(
    host="localhost",
    user="intern2",
    password="hogehoge-123",
    port=3306,
    database="intern2",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)


class Database(object):
    def __init__(self):
        self.log = Log()
        self.code = LocationCode()
        return

    def reconnect(self):
        connection = pymysql.connect(
            host="localhost",
            user="intern2",
            password="hogehoge-123",
            port=3306,
            database="intern2",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        return connection

    def checkUserId(self, id):
        connection = self.reconnect()
        cursor = connection.cursor()
        sql = f"SELECT COUNT(userId) FROM users WHERE userId = '{id}'"
        cursor.execute(sql)
        user_id = cursor.fetchall()

        if user_id[0]["COUNT(userId)"] == 0:
            sql = "INSERT INTO users (userId, middle_class_name, small_class_name, detail_class_name, region_class_name, locate_option) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (id, "NULL", "NULL", "NULL", "NULL", "NULL"))

        else:
            sql = "UPDATE users SET middle_class_name=%s, small_class_name=%s, detail_class_name=%s, region_class_name=%s, city_state=%s, detail_state=%s, locate_option=%s WHERE userId=%s"
            cursor.execute(sql, ("NULL", "NULL", "NULL", "NULL", 0, 0, "NULL", id))

        connection.commit()
        cursor.close()
        connection.close()

    # ユーザからのメッセージが地方かどうか
    def checkResion(self, id, message):
        connection = self.reconnect()
        cursor = connection.cursor()
        sql = (
            "SELECT region_number FROM regions,users WHERE regions.region_class_name=%s"
        )
        cursor.execute(sql, (message))
        response = cursor.fetchall()

        if len(response) == 0:
            return False
        else:
            sql = "UPDATE users SET region_class_name=%s where userId=%s"
            cursor.execute(sql, (message, id))
            connection.commit()

        cursor.close()
        connection.close()
        return True

        # ユーザからのメッセージが都道府県かどうか

    def checkPrefecture(self, id, message):
        connection = self.reconnect()
        cursor = connection.cursor()
        sql = "SELECT prefecture_number FROM prefectures,users WHERE prefectures.middle_class_name=%s"
        cursor.execute(sql, (message))
        response = cursor.fetchall()

        if len(response) == 0:
            return False
        else:
            sql = "UPDATE users SET middle_class_name=%s where userId=%s"
            cursor.execute(sql, (message, id))
            connection.commit()

        cursor.close()
        connection.close()
        return True

    # ユーザからのメッセージが市かどうか
    def checkCity(self, id, message):
        connection = self.reconnect()
        cursor = connection.cursor()
        sql = "SELECT city_number FROM citys,users WHERE citys.small_class_name=%s"
        cursor.execute(sql, (message))
        response = cursor.fetchall()

        if len(response) == 0:
            return False
        else:
            sql = "UPDATE users SET small_class_name=%s where userId=%s"
            cursor.execute(sql, (message, id))
            connection.commit()

        cursor.close()
        connection.close()
        return True

    # ユーザからのメッセージが詳細かどうか
    def checkDetail(self, id, message):
        connection = self.reconnect()
        cursor = connection.cursor()
        sql = (
            "SELECT detail_number FROM details,users WHERE details.detail_class_name=%s"
        )

        cursor.execute(sql, (message))
        response = cursor.fetchall()

        if len(response) == 0:
            return False
        else:
            sql = "UPDATE users SET detail_class_name=%s where userId=%s"
            cursor.execute(sql, (message, id))
            connection.commit()

        cursor.close()
        connection.close()
        return True

    def getPrefecture(self, id):
        connection = self.reconnect()
        cursor = connection.cursor()
        sql = "SELECT region_number FROM regions, users WHERE regions.region_class_name = users.region_class_name AND users.userId=%s"
        cursor.execute(sql, (id))
        region_number = cursor.fetchall()[0]["region_number"]

        sql = "SELECT middle_class_name FROM prefectures WHERE region_number = %s"
        cursor.execute(sql, (region_number))
        prefecture_list = cursor.fetchall()

        cursor.close()
        connection.close()

        return prefecture_list

    def getCity(self, id, prefecture):
        connection = self.reconnect()
        cursor = connection.cursor()

        sql = "SELECT prefecture_number FROM prefectures, users WHERE prefectures.middle_class_name = users.middle_class_name AND users.userId=%s"
        cursor.execute(sql, (id))
        prefecture_number = cursor.fetchall()[0]["prefecture_number"]

        sql = "SELECT small_class_name FROM citys WHERE prefecture_number = %s"
        cursor.execute(sql, (prefecture_number))
        city_list = cursor.fetchall()

        if len(city_list) == 0:
            datas = []
            codes = self.code.getLocationCode()

            for i in range(len(codes)):
                if codes[i]["middleClass"][0]["middleClassName"] == prefecture:
                    datas = codes[i]["middleClass"][1]["smallClasses"]
                    break

            for data in datas:
                city = data["smallClass"][0]
                sql = "INSERT INTO citys (prefecture_number, small_class_name, small_class_code) VALUES (%s, %s, %s)"
                cursor.execute(
                    sql,
                    (prefecture_number, city["smallClassName"], city["smallClassCode"]),
                )
                connection.commit()
                # self.log.showLog(data["smallClass"][0])
            sql = "SELECT small_class_name FROM citys WHERE prefecture_number = %s"
            cursor.execute(sql, (prefecture_number))
            city_list = cursor.fetchall()

        cursor.close()
        connection.close()
        return city_list

    def getDetail(self, id, city):
        connection = self.reconnect()
        cursor = connection.cursor()

        sql = "SELECT city_number FROM citys, users WHERE citys.small_class_name = users.small_class_name AND users.userId=%s"
        cursor.execute(sql, (id))
        city_number = cursor.fetchall()[0]["city_number"]

        sql = "SELECT detail_class_name FROM details WHERE city_number = %s"
        cursor.execute(sql, (city_number))
        detail_list = cursor.fetchall()

        if len(detail_list) == 0:
            sql = "SELECT middle_class_name FROM users WHERE userId=%s"
            cursor.execute(sql, (id))
            prefecture = cursor.fetchall()[0]["middle_class_name"]

            datas = []
            detail_datas = []
            detail_list = []
            codes = self.code.getLocationCode()

            for i in range(len(codes)):
                if codes[i]["middleClass"][0]["middleClassName"] == prefecture:
                    datas = codes[i]["middleClass"][1]["smallClasses"]
                    break

            for data in datas:
                if data["smallClass"][0]["smallClassName"] == city:
                    if len(data["smallClass"]) > 1:
                        detail_datas = data["smallClass"][1]["detailClasses"]
                    break
            self.log.showLog(detail_datas)
            if len(detail_datas) > 0:
                for detail_data in detail_datas:
                    detail = detail_data["detailClass"]
                    sql = "INSERT INTO details (city_number, detail_class_name, detail_class_code) VALUES (%s, %s, %s)"
                    cursor.execute(
                        sql,
                        (
                            city_number,
                            detail["detailClassName"],
                            detail["detailClassCode"],
                        ),
                    )
                    connection.commit()

                sql = "SELECT detail_class_name FROM details WHERE city_number = %s"
                cursor.execute(sql, (city_number))
                detail_list = cursor.fetchall()

        cursor.close()
        connection.close()
        return detail_list

    def getPrefecturesParams(self, id):
        connection = self.reconnect()
        cursor = connection.cursor()
        sql = "SELECT middle_class_name, small_class_name, detail_class_name FROM users WHERE userId=%s"
        cursor.execute(sql, (id))
        response = cursor.fetchall()

        sql = "SELECT middle_class_code FROM prefectures WHERE middle_class_name = %s"
        cursor.execute(sql, (response[0]["middle_class_name"]))
        prefecture_result = cursor.fetchall()
        middle_class_code = prefecture_result[0]["middle_class_code"]

        sql = "SELECT small_class_code FROM citys WHERE small_class_name = %s"
        cursor.execute(sql, (response[0]["small_class_name"]))
        city_result = cursor.fetchall()
        small_class_code = city_result[0]["small_class_code"]

        sql = "SELECT detail_class_code FROM details WHERE detail_class_name = %s"
        cursor.execute(sql, (response[0]["detail_class_name"]))
        detail_result = cursor.fetchall()

        if len(detail_result) > 0:
            detail_class_code = detail_result[0]["detail_class_code"]
        else:
            detail_class_code = "NULL"

        cursor.close()
        connection.close()

        return middle_class_code, small_class_code, detail_class_code

    def updateCityState(self, id, value):
        connection = self.reconnect()
        cursor = connection.cursor()

        sql = "UPDATE users SET city_state=%s WHERE userId=%s"
        cursor.execute(sql, (value, id))

        connection.commit()
        sql = "SELECT middle_class_name FROM users WHERE userId=%s"
        cursor.execute(sql, (id))
        prefecture = cursor.fetchall()[0]["middle_class_name"]

        cursor.close()
        connection.close()
        return prefecture

    def updateDetailState(self, id, value):
        connection = self.reconnect()
        cursor = connection.cursor()

        sql = "UPDATE users SET detail_state=%s WHERE userId=%s"
        cursor.execute(sql, (value, id))

        connection.commit()
        sql = "SELECT small_class_name FROM users WHERE userId=%s"
        cursor.execute(sql, (id))
        city = cursor.fetchall()[0]["small_class_name"]

        cursor.close()
        connection.close()
        return city

    def updateLocateOption(self, id, option):
        connection = self.reconnect()
        cursor = connection.cursor()

        sql = "UPDATE users SET locate_option=%s WHERE userId=%s"
        cursor.execute(sql, (option, id))

        connection.commit()
        connection.close()
        cursor.close()

    def getLocateOption(self, id):
        connection = self.reconnect()
        cursor = connection.cursor()

        sql = "SELECT locate_option FROM users WHERE userId=%s"
        cursor.execute(sql, (id))

        locate_option = cursor.fetchall()[0]["locate_option"]
        connection.close()
        cursor.close()

        return locate_option
