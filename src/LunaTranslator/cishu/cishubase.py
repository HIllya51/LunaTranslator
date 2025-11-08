from myutils.config import globalconfig
from myutils.wrapper import threader
from myutils.utils import LRUCache
from traceback import print_exc
from myutils.commonbase import commonbase
import uuid
import inspect
from tinycss2 import parse_stylesheet, serialize
from tinycss2.ast import (
    WhitespaceToken,
    AtRule,
    QualifiedRule,
    ParseError,
    LiteralToken,
)


try:
    TYPE_CHECKING = False
    from typing import TYPE_CHECKING
except:
    pass
if TYPE_CHECKING:
    from qtsymbols import *


class DictTree:
    def text(self) -> str: ...
    def childrens(self) -> list: ...


class DictionaryRoot(DictTree):
    def menus(self, menu: "QMenu"): ...
    def tips(self) -> str: ...


class cishubase(commonbase):
    backgroundparser = ""
    use_github_md_css = False

    def init(self):
        pass

    def search(self, word) -> str: ...

    def getUrl(self, word) -> str: ...

    def result_cache_key(self, word, sentence=None):
        return word, sentence, str(self.rawconfig)

    def search_XX(self, word, sentence):
        sig = inspect.signature(self.search)
        params = sig.parameters
        if len(params) == 1:
            return self.search(word)
        elif len(params) == 2:
            return self.search(word, sentence)

    @property
    def canGetUrl(self) -> bool:
        return self.gconfig.get("canGetUrl", True)

    def __init__(self, typename) -> None:
        super().__init__(typename)
        self.callback = print
        self.__cache_results = LRUCache(32)
        self.needinit = True
        try:
            self.init()
            self.needinit = False
        except:
            print_exc()

    _globalconfig_key = "cishu"
    _setting_dict = globalconfig["cishu"]

    @threader
    def safesearch(self, callback, word, sentence=None):
        if self.needinit:
            self.init()
            self.needinit = False
        key = self.result_cache_key(word, sentence)
        if key:
            cacheresult = self.__cache_results.get(key)
            if cacheresult:
                callback(cacheresult)
                return
        try:
            res = self.multiapikeywrapper(self.search_XX)(word, sentence)
        except:
            print_exc()
            self.needinit = True
            res = None
        if res:
            callback(res)
            if key:
                self.__cache_results.put(key, res)
        else:
            callback(None)

    def __parseaqr(self, rule: QualifiedRule, divclass):
        start = True
        idx = 0
        skip = False
        skiproot = False
        for token in rule.prelude.copy():
            if skiproot:
                skiproot = False
                idx += 1
                continue
            if skip and token.type == "whitespace":
                skip = False
                idx += 1
                continue
            if start:
                if token.type == "ident" and token.value == "body":
                    # body
                    rule.prelude.insert(idx + 1, LiteralToken(0, 0, "." + divclass))
                    rule.prelude.insert(idx + 1, WhitespaceToken(0, 0, " "))
                    idx += 2
                else:
                    if token.type == "literal" and token.value == ":":
                        # :root
                        skiproot = True
                        idx += 1
                        continue
                    # .id tag
                    # tag
                    # #class tag
                    rule.prelude.insert(idx, WhitespaceToken(0, 0, " "))
                    rule.prelude.insert(idx, LiteralToken(0, 0, "." + divclass + " "))
                    idx += 2
                start = False
            elif token.type == "literal" and token.value == ",":
                # 有多个限定符
                start = True
                skip = True
            idx += 1

    def __parserules(self, rules, divclass):
        # print(stylesheet)
        for i, rule in enumerate(rules.copy()):
            if isinstance(rule, AtRule):
                if not rule.content:
                    # @charset "UTF-8";
                    continue
                internal = parse_stylesheet(rule.content, True, True)
                if len(internal) and isinstance(internal[0], ParseError):
                    # @font-face
                    continue
                # @....{ .klas{} }
                rule.content = self.__parserules(internal, divclass)
            elif isinstance(rule, QualifiedRule):
                self.__parseaqr(rules[i], divclass)
        return rules

    def parse_stylesheet(self, file_content: str, divclass=None):
        if divclass is None:
            _divclass = "luna" + str(uuid.uuid4())
        else:
            _divclass = divclass
        if file_content.startswith("<style>") and file_content.endswith("</style>"):
            file_content = file_content[7:-8]
        try:
            rules = parse_stylesheet(file_content, True, True)
            file_content = serialize(self.__parserules(rules, _divclass))
            # print(file_content)
        except:

            print_exc()
        if divclass is None:
            return file_content, _divclass
        else:
            return file_content
