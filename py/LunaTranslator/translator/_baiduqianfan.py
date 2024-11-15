from translator.basetranslator import basetrans
import json, requests
from traceback import print_exc
from myutils.utils import createenglishlangmap


class TS(basetrans):

    def langmap(self):
        return createenglishlangmap()

    def __init__(self, typename):
        self.context = []
        self.access = {}
        super().__init__(typename)

    def createdata(self, message):
        temperature = self.config["Temperature"]
        system = self._gptlike_createsys("use_user_prompt", "user_prompt")

        data = dict(
            system=system,
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=self.config["max_tokens"],
            n=1,
            # stop=None,
            top_p=self.config["top_p"],
            temperature=temperature,
            frequency_penalty=self.config["frequency_penalty"],
            stream=self.config["usingstream"],
        )
        return data

    def commonparseresponse(self, query, response: requests.ResponseBase, usingstream):
        if usingstream:
            message = ""
            for chunk in response.iter_lines():
                response_data = chunk.decode("utf-8").strip()
                if not response_data:
                    continue
                try:
                    json_data = json.loads(response_data[6:])
                    msg = json_data["result"].replace("\n\n", "\n").strip()
                    message += msg

                except:
                    print_exc()
                    raise Exception(response_data)
                yield msg
        else:
            try:
                message = response.json()["result"].replace("\n\n", "\n").strip()
            except:
                raise Exception(response)
            yield message
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": message})

    def get_access_token(self, API_KEY, SECRET_KEY):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": API_KEY,
            "client_secret": SECRET_KEY,
        }
        js = self.proxysession.post(url, params=params).json()

        try:
            return js["access_token"]
        except:
            raise Exception(js)

    def checkchange(self):
        self.checkempty(["model", "SECRET_KEY", "API_KEY"])
        SECRET_KEY, API_KEY = (
            self.multiapikeycurrent["SECRET_KEY"],
            self.multiapikeycurrent["API_KEY"],
        )
        if not self.access.get((API_KEY, SECRET_KEY)):
            acss = self.get_access_token(API_KEY, SECRET_KEY)
            self.access[(API_KEY, SECRET_KEY)] = acss
        return self.access[(API_KEY, SECRET_KEY)]

    def translate(self, query):
        acss = self.checkchange()
        query = self._gptlike_createquery(
            query, "use_user_user_prompt", "user_user_prompt"
        )
        message = []
        self._gpt_common_parse_context(
            message, self.context, self.config["context_num"]
        )
        message.append({"role": "user", "content": query})

        usingstream = self.config["usingstream"]
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{}?access_token={}".format(
            self.config["model"], acss
        )

        response = self.proxysession.post(
            url,
            json=self.createdata(message),
            stream=usingstream,
        )
        return self.commonparseresponse(query, response, usingstream)
