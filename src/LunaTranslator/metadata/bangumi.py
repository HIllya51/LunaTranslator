import requests, os
from myutils.config import static_data
import time, json, gobject
from qtsymbols import *
from metadata.abstract import common
from myutils.wrapper import threader


class bgmsettings(QWidget):
    """token 输入 + OAuth（折叠卡第一子项，fill 使编辑框尽量大）；
    校验信息为动态第二子项（取到后显示，见 bindinforow）。checkvalid
    在工作线程，控件更新经 _infosig 信号排队到 GUI 线程；本控件作为
    field 随子项入树存活（绑定方法的连接依赖实例存活）。"""

    _infosig = pyqtSignal(str)

    @property
    def headers(self):
        return {
            "Authorization": "Bearer " + self._ref.config["access-token"].strip(),
        }

    @property
    def username(self):
        response = requests.get(
            "https://api.bgm.tv/v0/me", headers=self.headers, proxies=self._ref.proxy
        )
        return response.json()["username"]

    @threader
    def checkvalid(self, k):
        # 工作线程：不直接动控件（旧版 setText 属越线程操作），信息经
        # _infosig 排队到 GUI 线程；输入过程中保留上次信息（不闪隐）
        t = time.time()
        self.tm = t
        if k != self._ref.config["access-token"]:
            self._ref.config["access-token"] = k
            self._ref.config["refresh_token"] = ""
        response = requests.post(
            "https://bgm.tv/oauth/token_status",
            params={"access_token": k},
            proxies=self._ref.proxy,
        ).json()
        if t != self.tm:
            return
        # print(response)
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
                # print(response1.json())
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
        else:
            info = " ".join(
                (response.get("error", ""), response.get("error_description", ""))
            )
        self._infosig.emit(info)

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
            # print(code)
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
            # print(response)
            access_token = response["access_token"]
            self._token.setText(access_token)
            self._ref.config["refresh_token"] = response["refresh_token"]
            self._ref.config["access-token"] = access_token
            # print(self._ref.config)
            break

    def __init__(self, _ref: common, gameuid: str) -> None:
        super().__init__()
        self.tm = None
        self._ref = _ref
        self.lbinfo = QLabel()
        self._showinfo = None
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        s = QLineEdit()
        s.textChanged.connect(self.checkvalid)
        s.setText(_ref.config["access-token"])
        self._token = s
        hbox.addWidget(s, 1)
        oauth = QPushButton("OAuth")
        hbox.addWidget(oauth)
        oauth.clicked.connect(self.__oauth)
        self._infosig.connect(self.__applyinfo)

    def bindinforow(self, show):
        """动态信息子项的显隐句柄（行式适配 addDynamicRow 的返回值）。"""
        self._showinfo = show

    def __applyinfo(self, info):
        # GUI 线程（checkvalid 在工作线程 emit，排队送达）
        self.lbinfo.setText(info)
        if self._showinfo is not None:
            self._showinfo(bool(info.strip()))


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
                # print(resp)
                self.config["refresh_token"] = ""

    def querysettingwindow(self, gameuid, layout):
        # layout 为行式适配（gui/gamemanager/setting.py _MetaSettingRows）：
        # 第一子项 = token 输入 + OAuth（fill：编辑框尽量大）；第二子项
        # 为动态信息行（取到信息后显示）
        bgm = bgmsettings(self, gameuid)
        layout.addRow("access-token", bgm, fill=True)
        bgm.bindinforow(layout.addDynamicRow(bgm.lbinfo))

    def getidbytitle(self, title):

        params = {
            "type": "4",
            "responseGroup": "small",
        }

        response = self.proxysession.get(
            "https://api.bgm.tv/search/subject/" + title, params=params
        )
        # print(response.text)
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

        headers = {}
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
        namemap = {}
        try:
            charas = self.proxysession.get(
                "https://api.bgm.tv/v0/subjects/{}/characters".format(sid),
                headers=headers,
            ).json()
            for _ in charas:
                # 目前取得的角色資訊不包含性別
                # 取得每個角色的性別須為每個角色分別呼叫：/v0/characters/{character_id}
                namemap[_["name"]] = {"name": _["name"], "sex": ""}
        except:
            pass
        return {
            "namemap": namemap,
            "title": response["name"],
            "images": [response["images"]["large"]],
            "webtags": vndbtags,
            "developers": developers,
            "description": response["summary"],
        }
