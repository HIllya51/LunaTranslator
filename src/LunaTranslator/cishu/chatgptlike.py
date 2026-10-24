from myutils.utils import (
    APIType,
    common_list_models,
    common_create_gemini_request,
    common_create_gpt_data,
)
import NativeUtils
import re
from myutils.proxy import getproxy
from cishu.cishubase import cishubase
from translator.gptcommon import (
    createheaders,
    stream_event_parser,
    parseresponsegemini,
    parseresponseclaude,
)
from gui.customparams import customparams, getcustombodyheaders
from language import Languages


def list_models(typename, regist):
    return common_list_models(
        getproxy(("cishu", typename)),
        APIType(regist["API接口地址"]()),
        regist["SECRET_KEY"]().split("|")[0],
    )


class Cishu(cishubase):
    use_github_md_css = True
    backgroundparser = 'document.querySelector("#luna_dict_internal_view article").style.backgroundColor="rgba(0,0,0,0)"'

    def init(self):
        self.maybeuse = {}

    def langmap(self):
        return Languages.createenglishlangmap()

    def result_cache_key(self, word, sentence=None):
        __ = {}
        __.update(self.rawconfig)
        if "modellistcache" in __:
            __.pop("modellistcache")
        return (word, sentence, str(__))

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

    def _wrap_gpt_result(self, resp, think=""):
        """结果后处理（search 的流式中间态与最终结果共用）：think 折叠
        块 + markdown 转 html。"""
        m = re.match(r"^<think>([\s\S]*?)</think>", resp)
        if m:
            think = (think + m.group(1)) if think else m.group(1)
            resp = resp[m.end() :]
        html = NativeUtils.Markdown2Html(resp)
        if think:
            html = (
                '<details style="border:2px solid"><summary style="text-align:center;background-color:pink;">Thinking</summary>{}</details>'.format(
                    NativeUtils.Markdown2Html(think)
                )
                + html
            )
        return html

    def _stream_request(self, apitype: APIType, sysprompt, query, extrabody, extraheader):
        """流式请求（三种 API 类型；强制 stream）"""
        headers = createheaders(
            apitype,
            self.multiapikeycurrent["SECRET_KEY"],
            self.maybeuse,
            self.proxy,
            extraheader,
        )
        if apitype == APIType.gemini:
            return common_create_gemini_request(
                self.proxysession,
                dict(self.config, **{"流式输出": True}),
                self.multiapikeycurrent["SECRET_KEY"],
                sysprompt,
                [{"role": "user", "parts": [{"text": query}]}],
                extraheader,
                extrabody,
                apitype,
            )
        if apitype == APIType.claude:
            message = [{"role": "user", "content": query}]
            data = dict(
                model=self.config["model"],
                messages=message,
                system=sysprompt,
                max_tokens=self.config["max_tokens"],
                stream=True,
            )
            if self.config.get("Temperature.use", True):
                data.update(temperature=self.config["Temperature"])
            data.update(extrabody)
            headers.update(extraheader)
            return self.proxysession.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                stream=True,
            )
        message = [{"role": "system", "content": sysprompt}]
        message.append({"role": "user", "content": query})
        _json = common_create_gpt_data(
            dict(self.config, **{"流式输出": True}), message, extrabody
        )
        return self.proxysession.post(
            apitype.finalurl(), headers=headers, json=_json, stream=True
        )

    def search(self, word, sentence=None):
        """流式查词：每个 delta 即 yield 当前累积的中间态。生成器自然
        结束即完成，最终结果=最后一个中间态（safesearch 只把最终结果
        落缓存/导出）。"""
        extrabody, extraheader = getcustombodyheaders(
            self.config.get("customparams"), **locals()
        )
        query = self._gptlike_createquery(
            word, sentence, "use_user_user_prompt", "user_user_prompt_1"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        apitype = APIType(self.config["API接口地址"])
        response = self._stream_request(
            apitype, sysprompt, query, extrabody, extraheader
        )
        think = ""
        acc = ""
        if apitype == APIType.gemini:
            # parseresponsegemini 已滤 thought 部分
            for delta in parseresponsegemini(response, False):
                acc += delta
                yield self._wrap_gpt_result(acc)
        elif apitype == APIType.claude:
            for delta in parseresponseclaude(response):
                acc += delta
                yield self._wrap_gpt_result(acc)
        else:
            isreasoning = False
            for json_data in stream_event_parser(response):
                try:
                    delta = json_data["choices"][0].get("delta", {})
                    msg = delta.get("content")
                    reasoning = delta.get("reasoning_content")
                    if reasoning:
                        isreasoning = True
                        think += reasoning
                    elif msg:
                        isreasoning = False
                        acc += msg
                    else:
                        continue
                    yield self._wrap_gpt_result(acc, think)
                except:
                    raise Exception(json_data)
