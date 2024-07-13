from ocrengines.baseocrclass import baseocr
import re, time


class OCR(baseocr):

    def ocr(self, imagebinary):
        # https://github.com/AuroraWright/owocr/blob/master/owocr/ocr.py

        regex = re.compile(r">AF_initDataCallback\(({key: 'ds:1'.*?)\);</script>")

        timestamp = int(time.time() * 1000)
        url = f"https://lens.google.com/v3/upload?stcs={timestamp}"
        headers = {
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryUjYOv45hug6CFh3t",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3771) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.144 Mobile Safari/537.36",
        }
        cookies = {"SOCS": "CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg"}

        data = (
            '------WebKitFormBoundaryUjYOv45hug6CFh3t\r\nContent-Disposition: form-data; name="encoded_image"; filename="screenshot.png"\r\nContent-Type: image/png\r\n\r\n'.encode(
                "latin-1"
            )
            + imagebinary
            + "\r\n------WebKitFormBoundaryUjYOv45hug6CFh3t--\r\n".encode("latin-1")
        )
        res = self.proxysession.post(
            url, data=data, headers=headers, cookies=cookies, timeout=20
        )
        match = regex.search(res.text)
        if match == None:
            raise Exception(False, "Regex error!")
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

        res = ""
        text = lens_object["data"][3][4][0]
        print(text)
        if len(text) > 0:
            lines = text[0]
            for line in lines:
                res += line + "\n"

        return "\n".join(["\n".join(_) for _ in text])
