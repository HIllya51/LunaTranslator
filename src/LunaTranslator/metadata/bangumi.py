import requests, os
from myutils.config import savehook_new_data, static_data
from myutils.utils import initanewitem, gamdidchangedtask
import functools, time, json, gobject
from qtsymbols import *
from metadata.abstract import common
from gui.gamemanager.dialog import getreflist, getalistname
from myutils.wrapper import threader
from gui.usefulwidget import threebuttons


class bgmsettings(QFormLayout):

    @property
    def headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Authorization": "Bearer " + self._ref.config["access-token"].strip(),
        }

    @property
    def username(self):
        response = requests.get(
            "https://api.bgm.tv/v0/me", headers=self.headers, proxies=self._ref.proxy
        )
        return response.json()["username"]

    def querylist(self):

        params = {
            "subject_type": "4",
            "limit": "30",
            "offset": "0",
        }
        collectresults = []
        response = requests.get(
            "https://api.bgm.tv/v0/users/{}/collections".format(self.username),
            params=params,
            headers=self.headers,
            proxies=self._ref.proxy,
        )
        for item in response.json()["data"]:
            collectresults.append(
                {"id": item["subject_id"], "name": item["subject"]["name"]}
            )
        return collectresults

    def getalistname_download(self, uid):

        reflist = getreflist(uid)
        collectresults = self.querylist()
        thislistvids = [
            savehook_new_data[gameuid].get(self._ref.idname, 0) for gameuid in reflist
        ]
        collect = {}
        for gameuid in savehook_new_data:
            vid = savehook_new_data[gameuid].get(self._ref.idname, 0)
            if not vid:
                continue
            collect[vid] = gameuid

        for item in collectresults:
            title = item["name"]
            vid = item["id"]
            if vid in thislistvids:
                continue

            if vid in collect:
                gameuid = collect[vid]
            else:
                gameuid = initanewitem(title)
                savehook_new_data[gameuid][self._ref.idname] = vid
                gamdidchangedtask(self._ref.typename, self._ref.idname, gameuid)
            reflist.insert(0, gameuid)

    def getalistname_upload(self, uid):
        reflist = getreflist(uid)
        vids = [item["id"] for item in self.querylist()]

        for gameuid in reflist:
            vid = savehook_new_data[gameuid].get(self._ref.idname, 0)
            if not vid:
                continue
            if vid in vids:
                continue

            requests.post(
                "https://api.bgm.tv/v0/users/-/collections/{}".format(vid),
                headers=self.headers,
                json={
                    "type": 4,
                    # "rate": 10,
                    # "comment": "string",
                    # "private": True,
                    # "tags": ["string"],
                },
                proxies=self._ref.proxy,
            )

    def singleupload_existsoverride(self, gameuid):
        vid = savehook_new_data[gameuid].get(self._ref.idname, 0)
        if not vid:
            return
        try:
            requests.post(
                "https://api.bgm.tv/v0/users/-/collections/{}".format(vid),
                headers=self.headers,
                json={
                    "type": 4,
                    # "rate": 10,
                    # "comment": "string",
                    # "private": True,
                    # "tags": ["string"],
                },
                proxies=self._ref.proxy,
            )
        except:
            pass

    showhide = pyqtSignal(bool)

    @threader
    def checkvalid(self, k):
        self.showhide.emit(False)
        self.lbinfo.setText("")
        t = time.time()
        self.tm = t
        if k != self._ref.config["access-token"]:
            self._ref.config["access-token"] = k
            self._ref.config["refresh_token"] = ""
        headers = {
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        response = requests.post(
            "https://bgm.tv/oauth/token_status",
            params={"access_token": k},
            headers=headers,
            proxies=self._ref.proxy,
        ).json()
        if t != self.tm:
            return
        print(response)
        expires = response.get("expires", 0)
        if expires:
            info = ""
            try:
                response1 = requests.get(
                    "https://api.bgm.tv/v0/me",
                    params={"access_token": k},
                    headers=self.headers,
                    proxies=self._ref.proxy,
                )
                print(response1.json())
                info += "用户名： " + response1.json()["nickname"] + "\n"
            except:
                pass
            try:
                create = (
                    json.loads(response["info"])
                    .get("created_at", "")
                    .replace("T", " ")
                    .split(".")[0]
                )
                if create:
                    info += "创建日期： " + create + " "
            except:
                pass
            info += "有效期至： " + time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(expires)
            )
            self.showhide.emit(True)
        else:
            info = " ".join(
                (response.get("error", ""), response.get("error_description", ""))
            )
            self.showhide.emit(False)
        self.lbinfo.setText(info)

    def __oauth(self):
        bangumioauth = gobject.getcachedir("bangumioauth")
        try:
            os.remove(bangumioauth)
        except:
            pass
        os.startfile(
            "https://bgm.tv/oauth/authorize?client_id={}&response_type=code&redirect_uri=lunatranslator://bangumioauth".format(
                static_data["bangumi_oauth"]["client_id"]
            )
        )
        self.__wait()

    @threader
    def __wait(self):
        bangumioauth = gobject.getcachedir("bangumioauth")
        while True:
            time.sleep(1)
            if not os.path.exists(bangumioauth):
                continue
            try:
                with open(bangumioauth, "r", encoding="utf8") as ff:
                    code = ff.read()
            except:
                continue
            print(code)
            os.remove(bangumioauth)
            response = requests.post(
                "https://bgm.tv/oauth/access_token",
                json={
                    "grant_type": "authorization_code",
                    "client_id": static_data["bangumi_oauth"]["client_id"],
                    "client_secret": static_data["bangumi_oauth"]["client_secret"],
                    "code": code,
                    "redirect_uri": "lunatranslator://bangumioauth",
                },
                proxies=self._ref.proxy,
            ).json()
            print(response)
            access_token = response["access_token"]
            self._token.setText(access_token)
            self._ref.config["refresh_token"] = response["refresh_token"]
            self._ref.config["access-token"] = access_token
            print(self._ref.config)
            break

    def __init__(self, layout: QVBoxLayout, _ref: common, gameuid: str) -> None:
        super().__init__(None)
        layout.addLayout(self)
        self.tm = None
        self._ref = _ref
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        s = QLineEdit()
        self.lbinfo = QLabel()
        s.textChanged.connect(self.checkvalid)
        s.setText(_ref.config["access-token"])
        ww = QWidget()
        fl2 = QFormLayout(ww)
        fl2.setContentsMargins(0, 0, 0, 0)
        ww.hide()
        self.fl2 = ww
        self.showhide.connect(self.fl2.setVisible)
        self._token = s
        vbox.addLayout(hbox)
        hbox.addWidget(s)
        oauth = QPushButton("OAuth")
        hbox.addWidget(oauth)
        oauth.clicked.connect(self.__oauth)
        vbox.addWidget(self.lbinfo)
        self.addRow("access-token", vbox)

        btn = threebuttons(["上传游戏", "上传游戏列表", "获取游戏列表"])
        btn.btn1clicked.connect(
            functools.partial(self.singleupload_existsoverride, gameuid)
        )
        btn.btn2clicked.connect(
            functools.partial(
                getalistname, btn, self.getalistname_upload, title="上传游戏列表"
            )
        )
        btn.btn3clicked.connect(
            functools.partial(
                getalistname, btn, self.getalistname_download, title="添加到列表"
            )
        )
        fl2.addRow(btn)
        self.addRow(ww)


class searcher(common):
    def __init__(self, typename) -> None:
        super().__init__(typename)
        self._refresh()

    @threader
    def _refresh(self):
        if self.config["refresh_token"]:
            resp = self.proxysession.post(
                "https://bgm.tv/oauth/access_token",
                json={
                    "grant_type": "refresh_token",
                    "client_id": static_data["bangumi_oauth"]["client_id"],
                    "client_secret": static_data["bangumi_oauth"]["client_secret"],
                    "refresh_token": self.config["refresh_token"],
                    "redirect_uri": "lunatranslator://bangumioauth",
                },
            ).json()
            try:
                self.config["refresh_token"] = resp["refresh_token"]
                self.config["access-token"] = resp["access_token"]
            except:
                print(resp)
                self.config["refresh_token"] = ""

    def querysettingwindow(self, gameuid, layout):
        bgmsettings(layout, self, gameuid)

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
        return "https://bangumi.tv/subject/{}".format(_id)

    def searchfordata(self, sid):

        headers = {
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        if self.config["access-token"].strip() != "":
            headers["Authorization"] = "Bearer " + self.config["access-token"]
        response = self.proxysession.get(
            "https://api.bgm.tv/v0/subjects/{}".format(sid), headers=headers
        )
        try:
            response = response.json()
        except:
            return {}

        vndbtags = [_["name"] for _ in response["tags"]]
        developers = []
        for _ in response["infobox"]:
            if _["key"] in ["游戏开发商", "开发", "发行"]:
                if isinstance(_["value"], str):
                    developers.append(_["value"])
                else:
                    for __ in _["value"]:
                        if isinstance(__, str):
                            developers.append(__)
                        elif isinstance(__, dict):
                            developers.append(__["v"])
        namemaps = {}
        try:
            charas = self.proxysession.get(
                "https://api.bgm.tv/v0/subjects/{}/characters".format(sid),
                headers=headers,
            ).json()
            for _ in charas:
                namemaps[_["name"]] = _["name"]
        except:
            pass
        return {
            "namemap": namemaps,
            "title": response["name"],
            "images": [response["images"]["large"]],
            "webtags": vndbtags,
            "developers": developers,
            "description": response["summary"].replace("\n", "<br>"),
        }
