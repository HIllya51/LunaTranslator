from myutils.proxy import getproxy
from myutils.utils import getlangtgt, getlangsrc, getlanguse, stringfyerror
from myutils.config import _TR, globalconfig
from myutils.wrapper import stripwrapper
from language import Languages
import requests, types


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
    def __init__(self, _key1, _key2, *a, **kw):
        super().__init__(*a, **kw)
        self.proxyconf = _key1, _key2

    def request(self, *args, **kwargs):
        kwargs["proxies"] = getproxy(self.proxyconf)

        return super().request(*args, **kwargs)


class multikeyhelper:
    @property
    def keyfrom(self): ...

    def __init__(self):
        self.multiapikeycurrentidx = -1
        self.delay_known_apikeys_num = 1
        self.apikey_skip_round = {}
        self.apikey_error_cnt = {}

    @property
    def multiapikeycurrent(self):

        class alternatedict(dict):
            def __getitem__(self2, __key):
                t = super().__getitem__(__key)
                if type(t) != str:
                    raise Exception("Incorrect use of multiapikeycurrent")
                if "|" in t:
                    ts = t.split("|")
                    self.multiapikeycurrentidx = self.multiapikeycurrentidx % len(ts)
                    self.delay_known_apikeys_num = len(ts)
                    t = ts[int(self.multiapikeycurrentidx)]
                return t.strip()

        return alternatedict(self.keyfrom)

    def __error_happend(self, curridx):
        if curridx not in self.apikey_error_cnt:
            self.apikey_error_cnt[curridx] = 0
            self.apikey_skip_round[curridx] = 0
        self.apikey_error_cnt[curridx] += 1
        self.apikey_skip_round[curridx] += self.apikey_error_cnt[curridx]

    def __before_query(self):
        while True:
            self.multiapikeycurrentidx += 1
            self.multiapikeycurrentidx = (
                self.multiapikeycurrentidx % self.delay_known_apikeys_num
            )
            if self.apikey_skip_round.get(self.multiapikeycurrentidx, 0):
                self.apikey_skip_round[self.multiapikeycurrentidx] -= 1
            else:
                break
        return self.multiapikeycurrentidx

    def multiapikeywrapper(self, func):
        def _wrapper(*args, **kwargs):
            try:
                curridx = self.__before_query()
                ret = func(*args, **kwargs)

                if isinstance(ret, types.GeneratorType):
                    return self.__generatorhelper(ret, curridx)
                else:
                    return ret
            except Exception as e:
                print(stringfyerror(e))
                self.__error_happend(curridx)
                raise e

        return _wrapper

    def __generatorhelper(self, ret, curridx):
        try:
            for _ in ret:
                yield _
        except GeneratorExit as e:
            raise e
        except Exception as e:
            self.__error_happend(curridx)
            raise e


class commonbase(multikeyhelper):
    _globalconfig_key = None
    _setting_dict = None
    typename = None

    @property
    def keyfrom(self):
        return self.config

    def langmap(self):
        return {}

    @property
    def proxy(self):
        return getproxy((self._globalconfig_key, self.typename))

    @property
    def is_src_auto(self):
        return self.srclang_1 == Languages.Auto

    needzhconv = False

    def checklangzhconv(self, lang, text):
        if not text:
            return text
        if Languages.TradChinese != lang:
            return text

        import zhconv

        return zhconv.convert(text, "zh-tw")

    def __getlang(self, l: Languages):
        if self.needzhconv and l == Languages.TradChinese:
            l = Languages.Chinese
        return self.langmap_.get(l, l.code)

    @property
    def srclang_1(self) -> Languages:
        return getlangsrc()

    @property
    def srclang(self):
        return self.__getlang(self.srclang_1)

    @property
    def tgtlang_1(self) -> Languages:
        return getlangtgt()

    @property
    def tgtlang(self):
        return self.__getlang(self.tgtlang_1)

    @property
    def gconfig(self) -> dict:
        return globalconfig[self._globalconfig_key].get(self.typename, {})

    @property
    def config(self):
        try:
            return stripwrapper(self._setting_dict[self.typename]["args"])
        except:
            return {}

    @property
    def argstype(self):
        try:
            return self._setting_dict[self.typename]["argstype"]
        except:
            return {}

    @property
    def rawconfig(self):
        try:
            return self._setting_dict[self.typename]["args"]
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
        super().__init__()
        self.typename = typename
        self.renewsesion()

    def renewsesion(self):
        self.proxysession = proxysession(self._globalconfig_key, self.typename)

    def smartparselangprompt(self, template: str):
        if template.isascii():
            template = template.replace("{srclang}", self.srclang)
            template = template.replace("{tgtlang}", self.tgtlang)
        else:
            template = template.replace("{srclang}", _TR(self.srclang_1.zhsname))
            template = template.replace("{tgtlang}", _TR(self.tgtlang_1.zhsname))
        return template
