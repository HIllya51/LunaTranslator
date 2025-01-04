from myutils.proxy import getproxy
from myutils.utils import getlangtgt, getlangsrc, getlanguse
from myutils.config import _TR
from myutils.wrapper import stripwrapper
from language import Languages
import requests


class ArgsEmptyExc(Exception):
    def __init__(self, valuelist) -> None:
        super().__init__(" , ".join(valuelist) + getlanguse().space + _TR("不能为空"))


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
        l = self.srclang_1
        return self.langmap_.get(l, l)

    @property
    def srclang_1(self) -> Languages:
        return getlangsrc()

    @property
    def tgtlang_1(self) -> Languages:
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
        return Languages.create_langmap(self.langmap())

    def __init__(self, typename) -> None:
        self.typename = typename
        self.renewsesion()
        self.level2init()

    def renewsesion(self):
        self.proxysession = proxysession(self._globalconfig_key, self.typename)

    def level2init(self):
        pass
