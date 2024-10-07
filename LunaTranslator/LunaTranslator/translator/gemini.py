from translator.basetranslator import basetrans
from myutils.utils import createenglishlangmap
import json, requests
from myutils.proxy import getproxy


class TS(basetrans):
    def langmap(self):
        return createenglishlangmap()

    def __init__(self, typename):
        self.context = []
        super().__init__(typename)

    def inittranslator(self):
        self.api_key = None

    def translate(self, query):
        self.checkempty(["SECRET_KEY", "model"])

        gen_config = {
            "generationConfig": {
                "stopSequences": [" \n"],
                "temperature": self.config["Temperature"],
            }
        }
        model = self.config["model"]
        query = self._gptlike_createquery(
            query, "use_user_user_prompt", "user_user_prompt"
        )
        safety = {
            "safety_settings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        }
        sysprompt = self._gptlike_createsys("use_custom_prompt", "custom_prompt")
        sys_message = {"systemInstruction": {"parts": {"text": sysprompt}}}
        message = []
        self._gpt_common_parse_context(message, self.context, self.config["context"])

        message.append({"role": "user", "parts": [{"text": query}]})
        prefill = self._gptlike_create_prefill("prefill_use", "prefill")
        if prefill:
            message.append({"role": "model", "parts": [{"text": prefill}]})
        contents = dict(contents=message)
        usingstream = self.config["usingstream"]
        payload = {**contents, **safety, **sys_message, **gen_config}
        res = self.proxysession.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{['generateContent','streamGenerateContent'][usingstream]}",
            params={"key": self.multiapikeycurrent["SECRET_KEY"]},
            json=payload,
            stream=usingstream,
        )
        if usingstream:
            line = ""
            for __x in res.iter_lines(decode_unicode=True):
                __x = __x.strip()
                if not __x.startswith('"text":'):
                    continue
                __x = json.loads("{" + __x + "}")["text"]
                yield __x
                line += __x

        else:
            try:
                line = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            except:
                raise Exception(res.text)
            yield line
        self.context.append({"role": "user", "parts": [{"text": query}]})
        self.context.append({"role": "model", "parts": [{"text": line}]})


def list_models(typename, regist):
    js = requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        params={"key": regist["SECRET_KEY"]().split("|")[0].strip()},
        proxies=getproxy(("fanyi", typename)),
        timeout=10,
    ).json()
    try:
        models = js["models"]
    except:
        raise Exception(js)
    mm = []
    for m in models:
        name: str = m["name"]
        supportedGenerationMethods: list = m["supportedGenerationMethods"]
        if "generateContent" not in supportedGenerationMethods:
            continue
        if name.startswith("models/"):
            name = name[7:]
        mm.append(name)
    return sorted(mm)
