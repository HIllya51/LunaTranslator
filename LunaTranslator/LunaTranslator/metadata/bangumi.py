from metadata.abstract import common
from gui.inputdialog import autoinitdialog, autoinitdialog_items


class searcher(common):
    def querysettingwindow(self, parent):
        items = autoinitdialog_items(self.config_all)
        autoinitdialog(parent, self.name, 800, items)

    def getidbytitle(self, title):

        headers = {
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }

        params = {
            "type": "4",
            "responseGroup": "small",
        }

        response = self.proxysession.get(
            "https://api.bgm.tv/search/subject/" + title, params=params, headers=headers
        )
        print(response.text)
        try:
            response = response.json()
        except:
            return None
        if len(response["list"]) == 0:
            return None
        return response["list"][0]["id"]

    def refmainpage(self, _id):
        return f"https://bangumi.tv/subject/{_id}"

    def searchfordata(self, sid):

        headers = {
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        if self.config["access-token"].strip() != "":
            headers["Authorization"] = "Bearer " + self.config["access-token"]
        response = self.proxysession.get(
            f"https://api.bgm.tv/v0/subjects/{sid}", headers=headers
        )
        print(response.text)
        try:
            response = response.json()
        except:
            return {}
        try:
            imagepath = self.dispatchdownloadtask(response["images"]["large"])
        except:
            imagepath = []

        vndbtags = [_["name"] for _ in response["tags"]]
        developers = []
        for _ in response["infobox"]:
            if _["key"] == "游戏开发商":
                developers = [_["value"]]
                break
        return {
            # "namemap": namemap,
            "title": response["name_cn"],
            "imagepath_all": [imagepath],
            "webtags": vndbtags,
            "developers": developers,
        }
