from translator.basetranslator import basetrans, GptTextWithDict, GptDict
import requests
import random
from translator.gptcommon import list_models
from myutils.utils import APIType
from translator.gptcommon import (
    createheaders,
    common_create_gpt_data,
    parsestreamresp,
    common_parse_normal_response,
)
from language import Languages
from gui.customparams import *


class TS(basetrans):

    def result_cache_key(self, src, tgt, sentence):
        __ = {}
        __.update(self.rawconfig)
        if "modellistcache" in __:
            __.pop("modellistcache")
        return (
            src,
            tgt,
            sentence,
            str(__),
            random.randint(0, int(20 * self.config["temperature"])),
        )

    def __init__(self, typename):
        super().__init__(typename)
        self.maybeuse = {}
        self.context = []
        self.__model = None

    def make_gpt_dict_text(self, gpt_dict: GptDict, needinfo=True, split="->"):
        gpt_dict_text_list = []
        for gpt in gpt_dict:
            src = gpt.src

            dst = self.checklangzhconv(self.srclang, gpt.dst)
            info = self.checklangzhconv(self.srclang, gpt.info)

            if info and needinfo:
                single = "{}{}{} #{}".format(src, split, dst, info)
            else:
                single = "{}{}{}".format(src, split, dst)
            gpt_dict_text_list.append(single)

        gpt_dict_raw_text = "\n".join(gpt_dict_text_list)
        return gpt_dict_raw_text

    def _gpt_common_parse_context_2(
        self, messages: list, context, contextnum, ja=False, native=False
    ):
        msgs: "list[str]" = []
        self._gpt_common_parse_context(msgs, context, contextnum)
        __ja, __zh = [], []
        for i, _ in enumerate(msgs):
            [__zh, __ja][i % 2 == 0].append(_.strip())
        if __ja:
            if ja:
                messages.append(
                    {
                        "role": "user",
                        "content": ("" if native else "将下面的日文文本翻译成中文：")
                        + "\n".join(__ja),
                    }
                )
            messages.append({"role": "assistant", "content": "\n".join(__zh)})

    def sakura_make_messages(
        self, contextnum, prompt_version, query, gpt_dict: GptDict = None
    ):
        if prompt_version == "SakuraLLM v0.9":
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
                }
            ]
            self._gpt_common_parse_context_2(messages, self.context, contextnum)
            messages.append(
                {"role": "user", "content": "将下面的日文文本翻译成中文：" + query}
            )
        elif prompt_version == "SakuraLLM v0.10":
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地使用给定的术语表以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，注意不要混淆使役态和被动态的主语和宾语，不要擅自添加原文中没有的代词，也不要擅自增加或减少换行。",
                }
            ]
            self._gpt_common_parse_context_2(messages, self.context, contextnum)
            gpt_dict_raw_text = self.make_gpt_dict_text(gpt_dict)
            content = (
                "根据以下术语表（可以为空）：\n"
                + gpt_dict_raw_text
                + "\n\n"
                + "将下面的日文文本根据上述术语表的对应关系和备注翻译成中文："
                + query
            )
            messages.append({"role": "user", "content": content})
        elif prompt_version == "SakuraLLM v1.0":
            messages = [
                {
                    "role": "system",
                    "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
                }
            ]
            self._gpt_common_parse_context_2(messages, self.context, contextnum, True)
            if gpt_dict:
                content = (
                    "根据以下术语表（可以为空）：\n"
                    + self.make_gpt_dict_text(gpt_dict)
                    + "\n"
                    + "将下面的日文文本根据对应关系和备注翻译成中文："
                    + query
                )
            else:
                content = "将下面的日文文本翻译成中文：" + query
            messages.append({"role": "user", "content": content})
        elif prompt_version in ("GalTransl", "SakuraLLM v1.5"):
            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是一个视觉小说翻译模型，可以通顺地使用给定的术语表以指定的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，注意不要混淆使役态和被动态的主语和宾语，不要擅自添加原文中没有的特殊符号，也不要擅自增加或减少换行。"
                        if prompt_version == "GalTransl"
                        else "你是一个日本二次元领域的日语翻译模型，可以流畅通顺地以日本轻小说/漫画/Galgame的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
                    ),
                }
            ]
            __gptdict = self.make_gpt_dict_text(gpt_dict)
            __msg = []
            self._gpt_common_parse_context_2(
                __msg, self.context, contextnum, True, True
            )
            __msg = __msg[1]["content"] if __msg else ""
            content = (
                (("历史翻译：" + __msg + "\n\n") if __msg else "")
                + (
                    (
                        "参考以下术语表（可为空，格式为src->dst #备注）\n"
                        + __gptdict
                        + "\n\n"
                    )
                    if __gptdict
                    else ""
                )
                + ("根据以上术语表的对应关系和备注，" if __gptdict else "")
                + ("结合历史剧情和上下文，" if __msg else "")
                + "将下面的文本从日文翻译成简体中文：\n"
                + query
            )
            messages.append({"role": "user", "content": content})
        return messages

    def hymt2_make_messages(self, query, gpt_dict: GptDict = None):
        if not gpt_dict:
            if self.tgtlang_1 in (Languages.Chinese, Languages.TradChinese):
                messages = [
                    {
                        "role": "user",
                        "content": f"将以下文本翻译成{self.tgtlang_1.zhsname},注意只需要输出翻译后的结果,不要额外解释:\n\n{query}",
                    }
                ]
            else:
                messages = [
                    {
                        "role": "user",
                        "content": f"Translate the following text into {self.tgtlang_1.engname}. Note that you should only output the translated result without any additional explanation:\n\n{query}",
                    }
                ]
        else:
            if self.tgtlang_1 in (Languages.Chinese, Languages.TradChinese):
                messages = [
                    {
                        "role": "user",
                        "content": f"""参考下面的翻译：
{self.make_gpt_dict_text(gpt_dict, False, '翻译成')}
将以下文本翻译为{self.tgtlang_1.zhsname}，注意只需要输出翻译后的结果，不要额外解释：\n\n{query}""",
                    }
                ]
            else:
                messages = [
                    {
                        "role": "user",
                        "content": f"""Reference the following translations:
{self.make_gpt_dict_text(gpt_dict, False, ' translates to ')}
Translate the following text into {self.tgtlang_1.engname}. Note that you must ONLY output the translated result without any additional explanation:\n\n{query}""",
                    }
                ]
        return messages

    def make_messages(self, prompt_version: str, query, gpt_dict: GptDict = None):
        contextnum = (
            self.config["append_context_num"] if self.config["use_context"] else 0
        )
        if prompt_version == "auto":
            sysprompt = self._gptlike_createsys(None, None)
            messages = [{"role": "system", "content": sysprompt}]
            messages.append({"role": "user", "content": query})
            self.needzhconv = False
        elif prompt_version == "GalTransl" or prompt_version.startswith("SakuraLLM"):
            messages = self.sakura_make_messages(
                contextnum, prompt_version, query, gpt_dict
            )
            self.needzhconv = True
        elif prompt_version == "Hy-MT2":
            messages = self.hymt2_make_messages(query, gpt_dict)
            self.needzhconv = False
        return messages

    def maybedetectprompttype(self, prompt_version):
        if prompt_version != "auto":
            return prompt_version
        for m in (self.config["model"], self.__model):
            if (not m) or (m == "sukinishiro"):
                continue
            mlow = m.lower()
            if "hy-mt2" in mlow:
                return "Hy-MT2"
            if "galtransl" in mlow:
                return "GalTransl"
            if "sakura" in mlow:
                if "qwen3-v1.5" in mlow:
                    return "SakuraLLM v1.5"
                if "qwen2.5-v1.0" in mlow:
                    return "SakuraLLM v1.0"
                if "v0.10" in mlow:
                    return "SakuraLLM v0.10"
                if "v0.9" in mlow:
                    return "SakuraLLM v0.9"
        return prompt_version

    def translate(self, query_: GptTextWithDict):
        self.checkempty("API接口地址")

        gpt_dict = query_.dictionary
        apitype = APIType(self.config.get("API接口地址", ""))
        prompt_version = self.maybedetectprompttype(self.config["prompt_version_1"])
        query = (
            query_.rawtext if prompt_version != "SakuraLLM v0.9" else query_.parsedtext
        )

        messages = self.make_messages(prompt_version, query, gpt_dict=gpt_dict)

        extrabody, extraheader = getcustombodyheaders(
            self.config.get("customparams"), **locals()
        )
        usingstream = self.config["流式输出"]

        headers = createheaders(
            apitype,
            "",
            self.maybeuse,
            self.proxy,
            extraheader,
        )
        _json = common_create_gpt_data(self.config, messages, extrabody)
        response = self.proxysession.post(
            apitype.finalurl(), headers=headers, json=_json, stream=usingstream
        )
        getmodelhook = []
        try:
            if usingstream:
                respmessage = yield from parsestreamresp(
                    apitype,
                    response,
                    True,
                    False,
                    self.config["model"],
                    getmodelhook=getmodelhook,
                )
            else:
                respmessage = common_parse_normal_response(
                    response, apitype, hidethinking=True, getmodelhook=getmodelhook
                )
                yield respmessage
        except requests.exceptions.RequestException:
            raise ValueError("无法连接，可能未正确部署Sakura模型")
        self.__model = getmodelhook[0] if getmodelhook else self.config["model"]
        if not (query.strip() and respmessage.strip()):
            return
        self.context.append(query)
        self.context.append(respmessage)
