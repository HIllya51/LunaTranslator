from translator.basetranslator import basetrans
from translator.cdp_helper import cdp_helper
import random
import time, json
from urllib.parse import quote
from language import Languages


def getRandomNumber():
    src = random.Random()
    src.seed(time.time())
    num = 8300000 + src.randint(0, 99999)
    return num * 1000


def getICount(translate_text: str):
    return translate_text.count("i")


def getTimeStamp(i_count):
    ts = int(time.time() * 1000)
    if i_count != 0:
        i_count += 1
        return ts - (ts % i_count) + i_count
    else:
        return ts


def initDeepLXData(sourceLang: str, targetLang: str):
    hasRegionalVariant = False
    targetLangParts = targetLang.split("-")

    # targetLang can be "en", "pt", "pt-PT", "pt-BR"
    # targetLangCode is the first part of the targetLang, e.g. "pt" in "pt-PT"
    targetLangCode = targetLangParts[0]
    if len(targetLangParts) > 1:
        hasRegionalVariant = True

    commonJobParams = dict(
        wasSpoken=False,
        transcribe_as="",
    )
    if hasRegionalVariant:
        commonJobParams.update(dict(RegionalVariant=targetLang))
    return dict(
        jsonrpc="2.0",
        method="LMT_handle_texts",
        params=dict(
            splitting="newlines",
            lang=dict(
                source_lang_user_selected=sourceLang,
                target_lang=targetLangCode,
            ),
            commonJobParams=commonJobParams,
        ),
    )


class cdp_deepl(cdp_helper):
    target_url = "https://www.deepl.com/en/translator"

    @property
    def using(self):
        return self.ref.using and self.config["usewhich"] == 2

    @property
    def srclang(self):
        if self.ref.srclang_1 == Languages.TradChinese:
            return "zh"
        return self.ref.srclang_1

    @property
    def tgtlang(self):
        if self.ref.tgtlang_1 == Languages.TradChinese:
            return "zh-hant"
        return self.ref.tgtlang_1

    def translate(self, content):
        if self.ref.is_src_auto:
            self.Runtime_evaluate(
                'document.querySelector("#translator-source-clear-button").click()'
            )
            self.Runtime_evaluate(
                "document.getElementsByTagName('d-textarea')[0].focus()"
            )
            self.send_keys(content)
            result = self.wait_for_result(
                'document.getElementsByTagName("d-textarea")[1].textContent',
                ("complete", ""),
                multi=True,
            )
            while True:
                href: str = self.wait_for_result("window.location.href")
                try:
                    src, tgt = href.split("#")[1].split("/")[:2]
                    break
                except:
                    time.sleep(0.1)
            if tgt != self.tgtlang:
                self.Page_navigate(
                    "https://www.deepl.com/en/translator#{}/{}/{}".format(
                        src, self.tgtlang, quote(content)
                    )
                )
                return self.wait_for_result(
                    'document.getElementsByTagName("d-textarea")[1].textContent',
                    ("complete", ""),
                    multi=True,
                )
            else:
                return result

        else:
            self.Page_navigate(
                "https://www.deepl.com/en/translator#{}/{}/{}".format(
                    self.srclang, self.tgtlang, quote(content)
                )
            )
            return self.wait_for_result(
                'document.getElementsByTagName("d-textarea")[1].textContent',
                ("complete", ""),
                multi=True,
            )


class TS(basetrans):
    def init(self):
        self.devtool = None
        if self.config["usewhich"] == 2:
            self.devtool = cdp_deepl(self)

    @property
    def srclang(self):
        if self.srclang_1 == Languages.TradChinese:
            return "ZH"
        return self.srclang_1.upper()

    @property
    def tgtlang(self):
        if self.tgtlang_1 == Languages.TradChinese:
            return "ZH-HANT"
        return self.tgtlang_1.upper()

    def translate(self, translateText):
        if self.config["usewhich"] == 0:
            return self.translate_deeplx_internal(translateText)
        elif self.config["usewhich"] == 1:

            return self.translate_via_deeplx(translateText)
        elif self.config["usewhich"] == 2:
            if not self.devtool:
                self.devtool = cdp_deepl(self)
            return self.devtool.translate(translateText)

    def translate_via_deeplx(self, query):
        self.checkempty(["api"])
        payload = {
            "text": query,
            "source_lang": self.srclang,
            "target_lang": self.tgtlang,
        }

        response = self.proxysession.post(self.multiapikeycurrent["api"], json=payload)

        try:
            return response.json()["data"]
        except:
            raise Exception(response)

    def translate_deeplx_internal(self, translateText):
        # Preparing the request data for the DeepL API
        www2URL = "https://www2.deepl.com/jsonrpc"
        id = getRandomNumber() + 1
        postData = initDeepLXData(self.srclang, self.tgtlang)
        text = dict(
            text=translateText,
            requestAlternatives=3,
        )
        postData["id"] = id
        postData["params"]["texts"] = [text]
        postData["params"]["timestamp"] = getTimeStamp(getICount(translateText))

        # Marshalling the request data to JSON and making necessary string replacements

        postStr = json.dumps(postData)

        # Adding spaces to the JSON string based on the ID to adhere to DeepL's request formatting rules
        if (id + 5) % 29 == 0 or (id + 3) % 13 == 0:
            postStr = postStr.replace('"method":"', '"method" : "', -1)
        else:
            postStr = postStr.replace('"method":"', '"method": "', -1)

        res = self.proxysession.post(
            www2URL,
            headers={
                "Content-Type": "application/json",
                "Accept": "*/*",
                "x-app-os-name": "iOS",
                "x-app-os-version": "16.3.0",
                "Accept-Language": "en-US,en;q=0.9",
                "x-app-device": "iPhone13,2",
                "User-Agent": "DeepL-iOS/2.9.1 iOS 16.3.0 (iPhone13,2)",
                "x-app-build": "510265",
                "x-app-version": "2.9.1",
                "Connection": "keep-alive",
            },
            data=postStr,
        )
        try:
            return res.json()["result"]["texts"][0]["text"]
        except:
            raise Exception(res)
