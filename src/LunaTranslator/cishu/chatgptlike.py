from myutils.utils import (
    APIType,
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
        APIType(regist["API接口地址"]()),
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

    def search_1(self, apitype: APIType, sysprompt, query, extrabody, extraheader):
        message = [{"role": "system", "content": sysprompt}]
        message.append({"role": "user", "content": query})
        headers = createheaders(
            apitype,
            self.multiapikeycurrent["SECRET_KEY"],
            self.maybeuse,
            self.proxy,
            extraheader,
        )
        _json = common_create_gpt_data(self.config, message, extrabody)
        stream = self.config.get("流式输出", False)
        response = self.proxysession.post(
            apitype.finalurl(), headers=headers, json=_json, stream=stream
        )
        return response

    def _gptlike_createsys(self, usekey, tempk):
        default = "You are a professional dictionary assistant whose task is to help users search for information such as the meaning, pronunciation, etymology, synonyms, antonyms, and example sentences of {srclang} words. \nYou should be able to handle queries in multiple languages and provide in-depth information or simple definitions according to user needs. You should reply in {tgtlang}.\nThe user may provide the sentence in which the word is located. If the user provides the sentence in which the word is located, the semantics of the word in the sentence should also be analyzed."
        template = self.config[tempk] if self.config.get(usekey) else None
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

    def __format_html_dict(self, text, think=None):
        import re
        hidethinking = self.config.get("hidethinking", True)
        if hidethinking:
            text = re.sub(r"<think>[\s\S]*?</think>\n*", "", text)
            if "<think>" in text:
                text = re.sub(r"<think>[\s\S]*$", "<i>thinking...</i>", text)
            resp = text
            think = None
        else:
            if not think:
                pieces = re.split(r"<think>([\s\S]*?)</think>", text)
                if len(pieces) == 1:
                    resp = pieces[0]
                    if "<think>" in resp:
                        parts = resp.split("<think>", 1)
                        resp = parts[0]
                        think = parts[1]
                else:
                    think, resp = pieces[1], pieces[2]
            else:
                resp = text
        
        if self.config.get("markdown2html", True):
            resp = NativeUtils.Markdown2Html(resp)
            if think:
                think = NativeUtils.Markdown2Html(think)
        
        if think:
            think = '<details style="border:2px solid" open><summary style="text-align:center;background-color:pink;">Thinking</summary>{}</details>'.format(think)
            resp = think + resp
        return resp

    def search(self, word, sentence=None):
        extrabody, extraheader = getcustombodyheaders(
            self.config.get("customparams"), **locals()
        )
        query = self._gptlike_createquery(
            word, sentence, "use_user_user_prompt", "user_user_prompt_1"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        apitype = APIType(self.config.get("API接口地址", ""))
        if apitype == APIType.gemini:
            resp = self.query_gemini(apitype, sysprompt, query, extrabody, extraheader)
        elif apitype == APIType.claude:
            resp = self.query_cld(sysprompt, query, extrabody, extraheader)
        else:
            resp = self.search_1(apitype, sysprompt, query, extrabody, extraheader)
        
        usingstream = self.config.get("流式输出", False)
        if usingstream:
            from translator.gptcommon import parsestreamresp
            def dict_streamer():
                # We use hidethinking=False locally to receive <think> in chunks, then post-process
                gen = parsestreamresp(apitype, resp, False, False, self.config.get("model", ""))
                cumulative = ""
                for chunk in gen:
                    cumulative += chunk
                    yield self.__format_html_dict(cumulative)
            return dict_streamer()
        else:
            think, resp_str = common_parse_normal_response(resp, apitype, splitthink=True)
            return self.__format_html_dict(resp_str, think=think)

    def query_cld(self, sysprompt, query, extrabody, extraheader):
        temperature = self.config.get("Temperature", 0.3)

        message = []
        message.append({"role": "user", "content": query})
        headers = {
            "anthropic-version": "2023-06-01",
            "accept": "application/json",
            "X-Api-Key": self.multiapikeycurrent["SECRET_KEY"],
        }
        stream = self.config.get("流式输出", False)
        data = dict(
            model=self.config.get("model", ""),
            messages=message,
            system=sysprompt,
            max_tokens=self.config.get("max_tokens", 4096),
            temperature=temperature,
            stream=stream,
        )
        data.update(extrabody)
        headers.update(extraheader)
        response = self.proxysession.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            stream=stream,
        )
        return response

    def query_gemini(self, apitype, sysprompt, query, extrabody, extraheader):
        return common_create_gemini_request(
            self.proxysession,
            self.config,
            self.multiapikeycurrent["SECRET_KEY"],
            sysprompt,
            [{"role": "user", "parts": [{"text": query}]}],
            extraheader,
            extrabody,
            apitype,
        )
