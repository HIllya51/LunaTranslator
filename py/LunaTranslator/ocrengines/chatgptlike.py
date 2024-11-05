from ocrengines.baseocrclass import baseocr
import base64, requests
from myutils.utils import createurl, createenglishlangmap, urlpathjoin
from myutils.proxy import getproxy


def list_models(typename, regist):
    resp = requests.get(
        urlpathjoin(
            createurl(regist["apiurl"]().strip())[: -len("chat/completions")],
            "models",
        ),
        headers={
            "Authorization": "Bearer " + regist["SECRET_KEY"]().split("|")[0].strip()
        },
        proxies=getproxy(("ocr", typename)),
    )
    try:
        return sorted([_["id"] for _ in resp.json()["data"]])
    except:
        raise Exception(resp.maybejson)


class OCR(baseocr):

    def langmap(self):
        return createenglishlangmap()

    def createdata(self, message):
        temperature = self.config["Temperature"]

        data = dict(
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=self.config["max_tokens"],
            n=1,
            # stop=None,
            top_p=self.config["top_p"],
            temperature=temperature,
            frequency_penalty=self.config["frequency_penalty"],
        )
        return data

    def createheaders(self):
        return {"Authorization": "Bearer " + self.config["SECRET_KEY"]}

    def ocr(self, imagebinary):

        if self.config["use_custom_prompt"]:
            prompt = self.config["custom_prompt"]
        else:
            prompt = f"Recognize the {self.srclang} text in the picture."

        base64_image = base64.b64encode(imagebinary).decode("utf-8")
        message = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low",
                        },
                    },
                ],
            }
        ]

        response = self.proxysession.post(
            self.createurl(),
            headers=self.createheaders(),
            json=self.createdata(message),
        )
        try:
            message = (
                response.json()["choices"][0]["message"]["content"]
                .replace("\n\n", "\n")
                .strip()
            )
            return message
        except:
            raise Exception(response.maybejson)

    def createurl(self):
        return createurl(self.config["apiurl"])
