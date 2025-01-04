from myutils.config import globalconfig
from myutils.wrapper import threader
from traceback import print_exc
from myutils.proxy import getproxy
from myutils.utils import SafeFormatter, getlangtgt, getlangsrc
from myutils.commonbase import ArgsEmptyExc, proxysession
import re, uuid
from tinycss2 import parse_stylesheet, serialize
from tinycss2.ast import (
    WhitespaceToken,
    AtRule,
    QualifiedRule,
    ParseError,
    LiteralToken,
)
from language import Languages


class DictTree:
    def text(self) -> str: ...
    def childrens(self) -> list: ...


class cishubase:
    typename = None

    def init(self):
        pass

    def search(self, word):
        return word

    @property
    def proxy(self):
        return getproxy(("cishu", self.typename))

    def __init__(self, typename) -> None:
        self.typename = typename
        self.proxysession = proxysession("cishu", self.typename)
        self.callback = print
        self.needinit = True
        try:
            self.init()
            self.needinit = False
        except:
            print_exc()

    @threader
    def safesearch(self, sentence, callback):
        try:
            if self.needinit:
                self.init()
                self.needinit = False
            try:
                res = self.search(sentence)
            except:
                print_exc()
                self.needinit = True
                res = None
            if res and len(res):
                callback(res)
            else:
                callback(None)
        except:
            pass

    @property
    def config(self):
        return globalconfig["cishu"][self.typename]["args"]

    def _gptlike_createquery(self, query, usekey, tempk):
        user_prompt = (
            self.config.get(tempk, "") if self.config.get(usekey, False) else ""
        )
        fmt = SafeFormatter()
        return fmt.format(user_prompt, must_exists="sentence", sentence=query)

    def _gptlike_createsys(self, usekey, tempk):

        fmt = SafeFormatter()
        if self.config[usekey]:
            template = self.config[tempk]
        else:
            template = "You are a professional dictionary assistant whose task is to help users search for information such as the meaning, pronunciation, etymology, synonyms, antonyms, and example sentences of {srclang} words. You should be able to handle queries in multiple languages and provide in-depth information or simple definitions according to user needs. You should reply in {tgtlang}."
        tgt = getlangtgt()
        src = getlangsrc()
        langmap = Languages.create_langmap(Languages.createenglishlangmap())
        tgtlang = langmap.get(tgt, tgt)
        srclang = langmap.get(src, src)
        return fmt.format(template, srclang=srclang, tgtlang=tgtlang)

    def checkempty(self, items):
        emptys = []
        for item in items:
            if (self.config[item]) == "":
                emptys.append(item)
        if len(emptys):
            emptys_s = []
            argstype = self.config.get("argstype", {})
            for e in emptys:
                name = argstype.get(e, {}).get("name", e)
                emptys_s.append(name)
            raise ArgsEmptyExc(emptys_s)

    def markdown_to_html(self, markdown_text: str):
        print(markdown_text)
        lines = markdown_text.split("\n")
        html_lines = []
        lastli = ""
        lideep = 0

        def switchli():
            nonlocal lideep, lastli
            while lideep:
                html_lines.append("</ul>")
                lideep -= 1
            lastli = ""

        for line in lines:
            if not line:
                continue
            m = re.match(r"#+ ", line)
            if m:
                switchli()
                html_lines.append(
                    "<h{hi}>{inner}</h{hi}>".format(
                        hi=m.span()[1] - 1, inner=line[m.span()[1] :]
                    )
                )
            else:

                def parsex(line):
                    line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
                    line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", line)
                    return line

                m = re.match(r" *[-\*] ", line)
                if m:
                    if lastli != m.group():
                        if len(lastli) < len(m.group()):
                            html_lines.append("<ul>")
                            lideep += 1
                        else:
                            html_lines.append("</ul>")
                            lideep -= 1
                        lastli = m.group()
                    html_lines.append("<li>{}</li>".format(parsex(line[m.span()[1] :])))
                else:
                    switchli()
                    html_lines.append("<p>{}</p>".format(parsex(line)))

        switchli()

        return "".join(html_lines)

    def __parseaqr(self, rule: QualifiedRule, divclass):
        start = True
        idx = 0
        skip = False
        for token in rule.prelude.copy():
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
