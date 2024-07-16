from ocrengines.baseocrclass import baseocr


class OCR(baseocr):

    def ocr(self, imagebinary):
        self.checkempty(["token"])

        headers = {
            "authority": "ocrserver.docsumo.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "origin": "https://www.zhihu.com",
            "pragma": "no-cache",
            "referer": "https://www.zhihu.com/",
            "sec-ch-ua": '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "token": self.config["token"],
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        }

        files = {"file": ("screenshot.png", imagebinary, "application/octet-stream")}
        response = self.proxysession.post(
            "https://ocrserver.docsumo.com/api/v1/ocr/extract/",
            headers=headers,
            files=files,
        )
        # print(response.json())
        try:

            _ = response.json()["data"]
            self.countnum()
            return _
        except:
            raise Exception(response.text)
