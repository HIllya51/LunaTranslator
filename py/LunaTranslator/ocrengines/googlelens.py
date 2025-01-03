from ocrengines.baseocrclass import baseocr
import re, time


class OCR(baseocr):

    def ocr(self, imagebinary):

        regex = re.compile(r">AF_initDataCallback\(({key: 'ds:1'.*?)\);</script>")

        timestamp = int(time.time() * 1000)
        url = "https://lens.google.com/v3/upload?stcs={}".format(timestamp)
        # https://github.com/AuroraWright/owocr/blob/master/owocr/ocr.py#L209C9-L209C204
        headers = {
            "User-Agent": "Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/538.1 (KHTML, like Gecko) Version/6.0 TV Safari/538.1 STvPlus/9e6462f14a056031e5b32ece2af7c3ca,gzip(gfe),gzip(gfe)"
        }
        cookies = {"SOCS": "CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg"}
        files = {"encoded_image": ("screenshot.png", imagebinary, "image/png")}
        res = self.proxysession.post(url, files=files, headers=headers, cookies=cookies)
        match = regex.search(res.text)
        if not match:
            return
        sideChannel = "sideChannel"
        null = None
        key = "key"
        # hash="hash"
        data = "data"
        true = True
        false = False
        lens_object = eval(match.group(1))
        if "errorHasStatus" in lens_object:
            raise Exception(False, "Unknown Lens error!")

        text = lens_object["data"][3][4][0]
        return text[0] if text else None
