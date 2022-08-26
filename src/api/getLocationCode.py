import requests

url = "https://app.rakuten.co.jp/services/api/Travel/GetAreaClass/20131024?format=json"
application_id = "1043478375665697187"


class LocationCode:
    def getLocationCode(self):
        params = {"applicationId": application_id}

        response = requests.get(url, params)
        code = response.json()
        code_shape = code["areaClasses"]["largeClasses"][0]["largeClass"][1][
            "middleClasses"
        ]
        return code_shape
