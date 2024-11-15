from myutils.proxy import getproxy
from myutils.utils import getlangtgt, getlangsrc, getlanguagespace
from myutils.config import _TR, static_data
from myutils.wrapper import stripwrapper
import requests


class ArgsEmptyExc(Exception):
    def __init__(self, valuelist) -> None:
        super().__init__(" , ".join(valuelist) + getlanguagespace() + _TR("不能为空"))


class maybejson:
    def __init__(self, _) -> None:
        self._ = _

    def __str__(self):
        try:
            return str(self._.json())
        except:
            return self._.text

    def __getattr__(self, t):
        return getattr(self._, t)

    @property
    def maybejson(self):
        return str(self)


class proxysession(requests.Session):
    def __init__(self, _key1, _key2):
        super().__init__()
        self.proxyconf = _key1, _key2

    def request(self, *args, **kwargs) -> maybejson:
        kwargs["proxies"] = getproxy(self.proxyconf)

        return maybejson(super().request(*args, **kwargs))


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
        l = self.srclang_1
        return self.langmap_.get(l, l)

    @property
    def srclang_1(self) -> str:
        return getlangsrc()

    @property
    def tgtlang_1(self) -> str:
        return getlangtgt()

    @property
    def tgtlang(self):
        l = self.tgtlang_1
        return self.langmap_.get(l, l)

    @property
    def config(self):
        try:
            return stripwrapper(self._setting_dict[self.typename]["args"])
        except:
            return {}

    def countnum(self, query=None):
        # 防报错兼容性留置
        pass

    def checkempty(self, items):
        emptys = []
        for item in items:
            if (self.config[item]) == "":
                emptys.append(item)
        if len(emptys):
            emptys_s = []
            argstype = self._setting_dict[self.typename].get("argstype", {})
            for e in emptys:
                name = argstype.get(e, {}).get("name", e)
                emptys_s.append(name)
            raise ArgsEmptyExc(emptys_s)

    @property
    def langmap_(self):
        _ = dict(
            zip(
                [_["code"] for _ in static_data["lang_list_all"]],
                [_["code"] for _ in static_data["lang_list_all"]],
            )
        )
        _.update({"cht": "zh", "auto": "auto"})
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
