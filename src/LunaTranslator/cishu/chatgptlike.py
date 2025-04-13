from myutils.utils import (
    createurl,
    common_list_models,
    common_parse_normal_response,
    markdown_to_html,
)
from myutils.proxy import getproxy
from cishu.cishubase import cishubase
from translator.gptcommon import createheaders


def list_models(typename, regist):
    return common_list_models(
        getproxy(("cishu", typename)),
        regist["API接口地址"](),
        regist["SECRET_KEY"]().split("|")[0],
    )


class chatgptlike(cishubase):
    def init(self):
        self.maybeuse = {}

    @property
    def apiurl(self):
        return self.config["API接口地址"].strip()

    def createdata(self, message):
        temperature = self.config["Temperature"]
        data = dict(
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=self.config["max_tokens"],
            # n=1,
            # stop=None,
            top_p=self.config["top_p"],
            temperature=temperature,
        )
        if self.config.get("frequency_penalty_use", False):
            data.update(dict(frequency_penalty=self.config["frequency_penalty"]))
        return data

    def search_1(self, sysprompt, query):

        message = [{"role": "system", "content": sysprompt}]
        message.append({"role": "user", "content": query})
        response = self.proxysession.post(
            self.createurl(),
            headers=self.createheaders(),
            json=self.createdata(message),
        )
        return response

    def search(self, word):
        query = self._gptlike_createquery(
            word, "use_user_user_prompt", "user_user_prompt"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        apiurl = self.config["API接口地址"]
        if apiurl.startswith("https://generativelanguage.googleapis.com"):
            resp = self.query_gemini(sysprompt, query)
        if apiurl.startswith("https://api.anthropic.com/v1/messages"):
            resp = self.query_cld(sysprompt, query)
        else:
            resp = self.search_1(sysprompt, query)
        return markdown_to_html(common_parse_normal_response(resp, apiurl))

    def createheaders(self):
        return createheaders(
            self.apiurl, self.multiapikeycurrent, self.maybeuse, self.proxy
        )

    def createurl(self):
        return createurl(self.apiurl)

    def query_cld(self, sysprompt, query):
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
        response = self.proxysession.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
        )
        return response

    def query_gemini(self, sysprompt, query):
        safety = {
            "safety_settings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_CIVIC_INTEGRITY",
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
        sys_message = {"systemInstruction": {"parts": {"text": sysprompt}}}
        contents = {"contents": [{"role": "user", "parts": [{"text": query}]}]}

        payload = {}
        payload.update(contents)
        payload.update(safety)
        payload.update(sys_message)
        payload.update(gen_config)

        # Set up the request headers and URL
        headers = {"Content-Type": "application/json"}
        # Send the request
        response = self.proxysession.post(
            "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}".format(
                self.config["model"], self.multiapikeycurrent["SECRET_KEY"]
            ),
            headers=headers,
            json=payload,
        )
        return response
