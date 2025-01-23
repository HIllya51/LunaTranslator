from urllib.parse import quote
import re
from cishu.cishubase import cishubase
from myutils.utils import get_element_by, simplehtmlparser
from myutils.config import isascii
from language import Languages


class youdao(cishubase):

    def search(self, word: str):
        lang = self.srclang
        if lang == Languages.Auto:
            if isascii(word):
                lang = Languages.English
            else:
                lang = Languages.Japanese
        url = "https://dict.youdao.com/result?word={}&lang={}".format(quote(word), lang)
        text = self.proxysession.get(url).text
        if not get_element_by("class", "word-head", text):
            return
        text = re.sub("<header([\\s\\S]*?)></header>", "", text)
        text = re.sub("<aside([\\s\\S]*?)></aside>", "", text)

        text = re.sub("<link([\\s\\S]*?)>", "", text)
        text = re.sub('<script([\\s\\S]*?)src="(.*?)"([\\s\\S]*?)</script>', "", text)
        text = re.sub('<div class="lang-tip-con"([\\s\\S]*?)</div>', "", text)

        text = text.replace(
            simplehtmlparser(text, "div", '<div class="footer_container"'), ""
        )
        text = text.replace(
            simplehtmlparser(text, "div", '<div class="user-feed_back"'), ""
        )
        text = text.replace("min-width: 960px", "")
        text = text.replace("min-width:960px", "")
        return text
