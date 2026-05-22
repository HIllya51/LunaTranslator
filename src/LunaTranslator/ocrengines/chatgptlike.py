from ocrengines.baseocrclass import baseocr, OCRResult
import base64
from language import Languages
from myutils.utils import (
    APIType,
    common_list_models,
    common_parse_normal_response,
    common_create_gemini_request,
    common_create_gpt_data,
)
from myutils.proxy import getproxy
from myutils.llmcard import resolve_llm_config
from gui.customparams import customparams, getcustombodyheaders


def list_models(typename, regist):
    return common_list_models(
        getproxy(("ocr", typename)),
        APIType(regist["apiurl"]()),
        regist["SECRET_KEY"]().split("|")[0],
    )


class OCR(baseocr):
    @property
    def keyfrom(self):
        return resolve_llm_config(self.config, "apiurl")

    def langmap(self):
        return Languages.createenglishlangmap()

    def createheaders(self, extraheader):
        h = {"Authorization": "Bearer " + self.multiapikeycurrent["SECRET_KEY"]}
        h.update(extraheader)
        return h

    def ocr_mistral(self, llm_config: dict, base64_image, extrabody, extraheader):
        payload = {
            "model": llm_config["model"],
            "document": {
                "type": "image_url",
                "image_url": "data:image/jpeg;base64,{}".format(base64_image),
            },
        }
        payload.update(extrabody)
        response = self.proxysession.post(
            "https://api.mistral.ai/v1/ocr",
            headers=self.createheaders(extraheader),
            json=payload,
        )
        try:
            texts = []
            for pages in response.json()["pages"]:
                texts.append(pages["markdown"])
            return {"text": texts}
        except:
            raise Exception(response)

    def ocr_gemini(
        self, llm_config: dict, apitype, prompt, base64_image, extrabody, extraheader
    ):
        return common_create_gemini_request(
            self.proxysession,
            llm_config,
            self.multiapikeycurrent["SECRET_KEY"],
            None,
            [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": "image/png",
                                "data": base64_image,
                            }
                        },
                    ]
                }
            ],
            extraheader,
            extrabody,
            apitype,
        )

    def ocr_normal(
        self,
        llm_config: dict,
        apitype: APIType,
        prompt,
        base64_image,
        extrabody,
        extraheader,
    ):

        message = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/jpeg;base64," + base64_image,
                            "detail": "low",
                        },
                    },
                ],
            }
        ]
        h = self.createheaders(extraheader)
        response = self.proxysession.post(
            apitype.finalurl(),
            headers=h,
            json=common_create_gpt_data(llm_config, message, extrabody),
        )
        return response

    def _gptlike_createsys(self, usekey, tempk):
        default = "Recognize the {srclang} text in the picture."
        template = self.config[tempk] if self.config[usekey] else None
        template = template if template else default
        isocrtranslate = "{tgtlang}" in template
        template = self.smartparselangprompt(template)
        return template, isocrtranslate

    def ocr(self, imagebinary):
        llm_config = resolve_llm_config(self.config, "apiurl")
        extrabody, extraheader = getcustombodyheaders(
            llm_config.get("customparams"), **locals()
        )
        prompt, isocrtranslate = self._gptlike_createsys(
            "use_custom_prompt", "custom_prompt"
        )
        base64_image = base64.b64encode(imagebinary).decode("utf-8")
        apitype = APIType(llm_config["apiurl"])
        if apitype == APIType.gemini:
            response = self.ocr_gemini(
                llm_config, apitype, prompt, base64_image, extrabody, extraheader
            )
        elif apitype == APIType.mistral:
            return self.ocr_mistral(llm_config, base64_image, extrabody, extraheader)
        else:
            response = self.ocr_normal(
                llm_config, apitype, prompt, base64_image, extrabody, extraheader
            )
        return OCRResult(
            texts=common_parse_normal_response(response, apitype),
            isocrtranslate=isocrtranslate,
        )
