from ocrengines.baseocrclass import baseocr
import re, time


class OCR(baseocr):

    def ocr(self, imagebinary):

        regex = re.compile(r">AF_initDataCallback\(({key: 'ds:1'.*?)\);</script>")

        timestamp = int(time.time() * 1000)
        url = "https://lens.google.com/v3/upload?stcs={}".format(timestamp)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        files = {"encoded_image": ("screenshot.png", imagebinary, "image/png")}
        res = self.proxysession.post(url, files=files, headers=headers)
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
