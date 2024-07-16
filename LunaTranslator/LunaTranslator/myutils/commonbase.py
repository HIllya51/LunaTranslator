from myutils.proxy import getproxy
from myutils.utils import getlangtgt, getlangsrc
from myutils.config import _TR, static_data
from myutils.wrapper import stripwrapper
import requests


class ArgsEmptyExc(Exception):
    def __init__(self, valuelist) -> None:
        super().__init__(" , ".join(valuelist) + _TR("不能为空"))


class proxysession(requests.Session):
    def __init__(self, _key1, _key2):
        super().__init__()
        self.proxyconf = _key1, _key2

    def request(self, *args, **kwargs):
        kwargs["proxies"] = getproxy(self.proxyconf)
        return super().request(*args, **kwargs)


class commonbase:
    _globalconfig_key = None
    _setting_dict = None
    typename = None

    def langmap(self):
        return {}

    @property
    def proxy(self):
        return getproxy((self._globalconfig_key, self.typename))

    @property
    def srclang(self):
        try:
            l = getlangsrc()
            return self.langmap_[l]
        except:
            return ""

    @property
    def srclang_1(self):
        try:
            l = getlangsrc()
            return l
        except:
            return ""

    @property
    def tgtlang(self):
        try:
            l = getlangtgt()
            return self.langmap_[l]
        except:
            return ""

    @property
    def config(self):
        try:
            return stripwrapper(self._setting_dict[self.typename]["args"])
        except:
            return {}

    def countnum(self, query=None):
        if "次数统计" in self._setting_dict[self.typename]["args"]:
            try:
                self._setting_dict[self.typename]["args"]["次数统计"] = str(
                    int(self.config["次数统计"]) + 1
                )
            except:
                self._setting_dict[self.typename]["args"]["次数统计"] = "1"
        if ("字数统计" in self._setting_dict[self.typename]["args"]) and query:
            try:
                self._setting_dict[self.typename]["args"]["字数统计"] = str(
                    int(self.config["字数统计"]) + len(query)
                )
            except:
                self._setting_dict[self.typename]["args"]["字数统计"] = str(len(query))

    def checkempty(self, items):
        emptys = []
        for item in items:
            if (self.config[item]) == "":
                emptys.append(item)
        if len(emptys):
            raise ArgsEmptyExc(emptys)

    @property
    def langmap_(self):
        _ = dict(
            zip(
                static_data["language_list_translator_inner"],
                static_data["language_list_translator_inner"],
            )
        )
        _.update({"cht": "zh"})
        _.update(self.langmap())
        return _

    def __init__(self, typename) -> None:
        self.typename = typename
        self.renewsesion()
        self.level2init()

    def renewsesion(self):
        self.proxysession = proxysession(self._globalconfig_key, self.typename)

    def level2init(self):
        pass
