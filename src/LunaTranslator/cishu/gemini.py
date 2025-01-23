import requests
from myutils.utils import urlpathjoin
from myutils.proxy import getproxy
from cishu.cishubase import cishubase


def list_models(typename, regist):
    js = requests.get(
        urlpathjoin(regist["BASE_URL"]().strip(), "v1beta/models"),
        params={"key": regist["SECRET_KEY"]().split("|")[0].strip()},
        proxies=getproxy(("fanyi", typename)),
    )
    try:
        models = js.json()["models"]
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


class gemini(cishubase):

    def search(self, word):
        self.checkempty(["SECRET_KEY", "model"])
        api_key = self.config["SECRET_KEY"]
        model = self.config["model"]
        query = self._gptlike_createquery(
            word, "use_user_user_prompt", "user_user_prompt"
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
        gen_config = {
            "generationConfig": {
                "stopSequences": [" \n"],
                "temperature": self.config["Temperature"],
            }
        }
        sysprompt = self._gptlike_createsys("use_custom_prompt", "custom_prompt")
        sys_message = {"systemInstruction": {"parts": {"text": sysprompt}}}
        contents = {"contents": [{"role": "user", "parts": [{"text": query}]}]}

        payload = {}
        payload.update(contents)
        payload.update(safety)
        payload.update(sys_message)
        payload.update(gen_config)

        # Set up the request headers and URL
        headers = {"Content-Type": "application/json"}
        # by default https://generativelanguage.googleapis.com/v1
        # Send the request
        response = self.proxysession.post(
            urlpathjoin(
                self.config["BASE_URL"],
                "v1beta/models/{}:generateContent?key={}".format(model, api_key),
            ),
            headers=headers,
            json=payload,
        )
        try:
            return self.markdown_to_html(
                response.json()["candidates"][0]["content"]["parts"][0]["text"]
            )
        except Exception as e:
            raise Exception(response) from e
