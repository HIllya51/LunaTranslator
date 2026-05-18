from myutils.utils import (
    APIType,
    common_list_models,
    common_create_gemini_request,
    common_parse_normal_response,
    common_create_gpt_data,
)
import NativeUtils
from myutils.proxy import getproxy
from myutils.llmcard import resolve_llm_config
from cishu.cishubase import cishubase
from translator.gptcommon import createheaders
from gui.customparams import customparams, getcustombodyheaders
from language import Languages
import random


def list_models(typename, regist):
    return common_list_models(
        getproxy(("cishu", typename)),
        APIType(regist["API接口地址"]()),
        regist["SECRET_KEY"]().split("|")[0],
    )


class chatgptlike(cishubase):
    use_github_md_css = True
    backgroundparser = 'document.querySelector("#luna_dict_internal_view > article").style.backgroundColor="rgba(0,0,0,0)"'

    @property
    def keyfrom(self):
        return resolve_llm_config(self.config)

    def init(self):
        self.maybeuse = {}

    def langmap(self):
        return Languages.createenglishlangmap()

    def result_cache_key(self, word, sentence=None):
        __ = {}
        __.update(self.rawconfig)
        if "modellistcache" in __:
            __.pop("modellistcache")
        llm_config = resolve_llm_config(self.config)
        if "modellistcache" in llm_config:
            llm_config.pop("modellistcache")
        temperature = random.randint(0, int(20 * llm_config["Temperature"]))
        __["llm_model_config"] = llm_config
        return (word, sentence, temperature, str(__))

    def search_1(
        self, llm_config: dict, apitype: APIType, sysprompt, query, extrabody, extraheader
    ):
        message = [{"role": "system", "content": sysprompt}]
        message.append({"role": "user", "content": query})
        headers = createheaders(
            apitype,
            self.multiapikeycurrent["SECRET_KEY"],
            self.maybeuse,
            self.proxy,
            extraheader,
        )
        _json = common_create_gpt_data(llm_config, message, extrabody)
        response = self.proxysession.post(
            apitype.finalurl(), headers=headers, json=_json
        )
        return response

    def _gptlike_createsys(self, usekey, tempk):
        default = "You are a professional dictionary assistant whose task is to help users search for information such as the meaning, pronunciation, etymology, synonyms, antonyms, and example sentences of {srclang} words. \nYou should be able to handle queries in multiple languages and provide in-depth information or simple definitions according to user needs. You should reply in {tgtlang}.\nThe user may provide the sentence in which the word is located. If the user provides the sentence in which the word is located, the semantics of the word in the sentence should also be analyzed."
        template = self.config[tempk] if self.config[usekey] else None
        template = template if template else default
        template = self.smartparselangprompt(template)
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
        llm_config = resolve_llm_config(self.config)
        extrabody, extraheader = getcustombodyheaders(
            llm_config.get("customparams"), **locals()
        )
        query = self._gptlike_createquery(
            word, sentence, "use_user_user_prompt", "user_user_prompt_1"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        apitype = APIType(llm_config["API接口地址"])
        if apitype == APIType.gemini:
            resp = self.query_gemini(
                llm_config, apitype, sysprompt, query, extrabody, extraheader
            )
        elif apitype == APIType.claude:
            resp = self.query_cld(llm_config, sysprompt, query, extrabody, extraheader)
        else:
            resp = self.search_1(
                llm_config, apitype, sysprompt, query, extrabody, extraheader
            )
        think, resp = common_parse_normal_response(resp, apitype, splitthink=True)
        resp = NativeUtils.Markdown2Html(resp)
        if think:
            think = '<details style="border:2px solid"><summary style="text-align:center;background-color:pink;">Thinking</summary>{}</details>'.format(
                NativeUtils.Markdown2Html(think)
            )
            resp = think + resp
        return resp

    def query_cld(self, llm_config: dict, sysprompt, query, extrabody, extraheader):
        temperature = llm_config["Temperature"]

        message = []
        message.append({"role": "user", "content": query})
        headers = {
            "anthropic-version": "2023-06-01",
            "accept": "application/json",
            "X-Api-Key": self.multiapikeycurrent["SECRET_KEY"],
        }
        data = dict(
            model=llm_config["model"],
            messages=message,
            system=sysprompt,
            max_tokens=llm_config["max_tokens"],
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

    def query_gemini(
        self, llm_config: dict, apitype, sysprompt, query, extrabody, extraheader
    ):
        return common_create_gemini_request(
            self.proxysession,
            llm_config,
            self.multiapikeycurrent["SECRET_KEY"],
            sysprompt,
            [{"role": "user", "parts": [{"text": query}]}],
            extraheader,
            extrabody,
            apitype,
        )
