from myutils.config import globalconfig
from myutils.wrapper import threader
from myutils.utils import LRUCache
from traceback import print_exc
from myutils.commonbase import commonbase
import uuid, hashlib
import inspect, types
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

    def search(self, word: str) -> str: ...

    def getUrl(self, word: str) -> str: ...

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

    @property
    def support_langs(self):
        # 支持的语言代码列表（如 ["ja"]）；未设置或为空表示不限定语言。
        return self.gconfig.get("langs")

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
    def safesearch(self, callback, word, sentence=None, on_chunk=None):
        """查词入口（流式/非流式统一）：引擎的 search 返回 str 一次性
        回调 callback；返回生成器则流式——每个中间态调 on_chunk(html)
        （仅显示，不落缓存），耗尽后以 return 值为最终结果回调
        callback（只有它进缓存/Anki——中间流式过程不导出）；生成器
        没有 return 时以最后一个中间态为最终结果（写自定义流式词典只
        需一路 yield）。on_chunk=None 时中间态被丢弃，只回调最终结果，
        与非流式无异。缓存命中直接 callback。"""
        if self.needinit:
            self.init()
            self.needinit = False
        key = hashlib.md5(str(self.result_cache_key(word, sentence)).encode()).digest()
        if key:
            cacheresult = self.__cache_results.get(key)
            if cacheresult:
                callback(cacheresult)
                return

        def _run():
            # 用普通函数消费生成器（multiapikeywrapper 对生成器的转发会
            # 丢 return 值）；错误照常抛给 wrapper 做多 key 轮换
            ret = self.search_XX(word, sentence)
            if not isinstance(ret, types.GeneratorType):
                return ret
            gen = ret
            last = None
            while True:
                try:
                    chunk = next(gen)
                except StopIteration as e:
                    if e.value is not None:
                        return e.value
                    # 没有显式 return：以最后一个中间态为最终结果
                    return last
                if chunk:
                    last = chunk
                    if on_chunk:
                        on_chunk(chunk)

        try:
            res = self.multiapikeywrapper(_run)()
            if res and not isinstance(res, Exception) and key:
                self.__cache_results.put(key, res)
            callback(res)
        except Exception as e:
            print_exc()
            self.needinit = True
            callback(e)

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
