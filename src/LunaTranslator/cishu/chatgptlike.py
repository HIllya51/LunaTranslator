from myutils.utils import (
    createurl,
    common_list_models,
    common_create_gemini_request,
    common_parse_normal_response,
    common_create_gpt_data,
)
import NativeUtils
from myutils.proxy import getproxy
from cishu.cishubase import cishubase
from translator.gptcommon import createheaders
from gui.customparams import customparams, getcustombodyheaders
from language import Languages
import random


def list_models(typename, regist):
    return common_list_models(
        getproxy(("cishu", typename)),
        regist["API接口地址"](),
        regist["SECRET_KEY"]().split("|")[0],
    )


class chatgptlike(cishubase):
    use_github_md_css = True
    backgroundparser = 'document.querySelector("#luna_dict_internal_view > article").style.backgroundColor="rgba(0,0,0,0)"'

    def init(self):
        self.maybeuse = {}

    def langmap(self):
        return Languages.createenglishlangmap()

    def result_cache_key(self, word, sentence=None):
        __ = {}
        __.update(self.rawconfig)
        if "modellistcache" in __:
            __.pop("modellistcache")
        temperature = random.randint(0, int(20 * self.config["Temperature"]))
        return (word, sentence, temperature, str(__))

    @property
    def apiurl(self):
        return self.config["API接口地址"].strip()

    def search_1(self, sysprompt, query, extrabody, extraheader):
        message = [{"role": "system", "content": sysprompt}]
        message.append({"role": "user", "content": query})
        headers = createheaders(
            self.apiurl,
            self.multiapikeycurrent["SECRET_KEY"],
            self.maybeuse,
            self.proxy,
            extraheader,
        )
        _json = common_create_gpt_data(self.config, message, extrabody)
        response = self.proxysession.post(self.createurl(), headers=headers, json=_json)
        return response

    def _gptlike_createsys(self, usekey, tempk):

        template = self.config[tempk] if self.config[usekey] else None
        template = template if template else self.argstype[tempk]["placeholder"]
        template = template.replace("{srclang}", self.srclang)
        template = template.replace("{tgtlang}", self.tgtlang)
        return template

    def _gptlike_createquery(self, query, sentence, usekey, tempk):
        user_prompt = (
            self.config.get(tempk, "") if self.config.get(usekey, False) else ""
        )
        user_prompt = user_prompt.lstrip()
        if "{word}" not in user_prompt:
            user_prompt += "{word}"
        user_prompt = user_prompt.replace("{word}", query)
        if sentence:
            if "{sentence}" not in user_prompt:
                user_prompt = "sentence: {sentence}\n" + user_prompt
            user_prompt = user_prompt.replace("{sentence}", sentence)
        return user_prompt

    def search(self, word, sentence=None):
        extrabody, extraheader = getcustombodyheaders(
            self.config.get("customparams"), **locals()
        )
        query = self._gptlike_createquery(
            word, sentence, "use_user_user_prompt", "user_user_prompt_1"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        apiurl = self.config["API接口地址"]
        if apiurl.startswith("https://generativelanguage.googleapis.com"):
            resp = self.query_gemini(sysprompt, query, extrabody, extraheader)
        elif apiurl.startswith("https://api.anthropic.com/v1/messages"):
            resp = self.query_cld(sysprompt, query, extrabody, extraheader)
        else:
            resp = self.search_1(sysprompt, query, extrabody, extraheader)
        think, resp = common_parse_normal_response(resp, apiurl, splitthink=True)
        resp = NativeUtils.Markdown2Html(resp)
        if think:
            think = '<details style="border:2px solid"><summary style="text-align:center;background-color:pink;">Thinking</summary>{}</details>'.format(
                NativeUtils.Markdown2Html(think)
            )
            resp = think + resp
        return resp

    def createurl(self):
        return createurl(self.apiurl)

    def query_cld(self, sysprompt, query, extrabody, extraheader):
        temperature = self.config["Temperature"]

        message = []
        message.append({"role": "user", "content": query})
        headers = {
            "anthropic-version": "2023-06-01",
            "accept": "application/json",
            "X-Api-Key": self.multiapikeycurrent["SECRET_KEY"],
        }
        data = dict(
            model=self.config["model"],
            messages=message,
            system=sysprompt,
            max_tokens=self.config["max_tokens"],
            temperature=temperature,
        )
        data.update(extrabody)
        headers.update(extraheader)
        response = self.proxysession.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
        )
        return response

    def query_gemini(self, sysprompt, query, extrabody, extraheader):
        return common_create_gemini_request(
            self.proxysession,
            self.config,
            self.multiapikeycurrent["SECRET_KEY"],
            sysprompt,
            [{"role": "user", "parts": [{"text": query}]}],
            extraheader,
            extrabody,
        )
