from ocrengines.baseocrclass import baseocr
import uuid, json


class OCR(baseocr):
    def langmap(self):
        return {"zh": "zh-CHS"}

    def ocr(self, imagebinary):

        cookies = {
            "ABTEST": "0|1716807064|v17",
            "SUID": "22005E72BE50A00A0000000066546598",
            "wuid": "1716807064590",
            "SUV": "1720043144694",
            "SNUID": "4A31C2546066423F20E0F4C8609D6C10",
            "FQV": "837174c34ee13ac891646aeeec5a8cfa",
            "translate.sess": "971ddb4a-0c83-4ea4-8058-271867f48e77",
            "SGINPUT_UPSCREEN": "1721149101013",
            "NEW_SUV": "1721149407274",
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7,ru;q=0.6",
            "Connection": "keep-alive",
            "Origin": "https://fanyi.sogou.com",
            "Referer": "https://fanyi.sogou.com/picture",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        files = {
            "fileData": ("blob", imagebinary, "image/jpeg"),
            "fuuid": (None, str(uuid.uuid4())),
            "extraData": (
                None,
                json.dumps(
                    {
                        "from": self.srclang,
                        "to": self.tgtlang,
                        "imageName": str(uuid.uuid4()) + ".png",
                    }
                ),
            ),
        }

        response = self.proxysession.post(
            "https://fanyi.sogou.com/api/transpc/picture/upload",
            cookies=cookies,
            headers=headers,
            files=files,
        )
        try:
            boxes = []
            text = []
            ts = []
            for line in response.json()["data"].get("result", []):
                boxes.append(
                    [
                        int(_)
                        for _ in (
                            line["frame"][0].split(",") + line["frame"][2].split(",")
                        )
                    ]
                )
                text.append(line["content"])
                ts.append(line["trans_content"])
            if self.config["Translate"]:
                return "<notrans>" + self.common_solve_text_orientation(boxes, ts)
            else:
                return self.common_solve_text_orientation(boxes, text)
        except:
            from traceback import print_exc

            print_exc()
            raise Exception(response.text)
