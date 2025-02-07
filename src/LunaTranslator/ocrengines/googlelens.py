from ocrengines.baseocrclass import baseocr
import re, time


class OCR(baseocr):

    def ocr(self, imagebinary):

        regex = re.compile(r">AF_initDataCallback\(({key: 'ds:1'.*?)\);</script>")

        fake_chromium_config = {
            "viewport": (1920, 1080),
            "major_version": "109",
            "version": "109.0.5414.87",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.87 Safari/537.36",
        }
        # https://github.com/AuroraWright/owocr/commit/aa0cba6ee5c18be04149afc1130044e27becd4b6
        url = "https://lens.google.com/v3/upload"
        params = {
            "ep": "ccm",  # EntryPoint
            "re": "dcsp",  # RenderingEnvironment - DesktopChromeSurfaceProto
            "s": "4",  # SurfaceProtoValue - Surface.CHROMIUM
            "st": str(int(time.time() * 1000)),
            "sideimagesearch": "1",
            "vpw": str(fake_chromium_config["viewport"][0]),
            "vph": str(fake_chromium_config["viewport"][1]),
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Origin": "https://lens.google.com",
            "Referer": "https://lens.google.com/",
            "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="{}", "Chromium";v="{}"'.format(
                fake_chromium_config["major_version"],
                fake_chromium_config["major_version"],
            ),
            "Sec-Ch-Ua-Arch": '"x86"',
            "Sec-Ch-Ua-Bitness": '"64"',
            "Sec-Ch-Ua-Full-Version": '"{}"'.format(fake_chromium_config["version"]),
            "Sec-Ch-Ua-Full-Version-List": '"Not A(Brand";v="99.0.0.0", "Google Chrome";v="{}", "Chromium";v="{}"'.format(
                fake_chromium_config["major_version"],
                fake_chromium_config["major_version"],
            ),
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Model": '""',
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Ch-Ua-Platform-Version": '"15.0.0"',
            "Sec-Ch-Ua-Wow64": "?0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": fake_chromium_config["user_agent"],
            "X-Client-Data": "CIW2yQEIorbJAQipncoBCIH+ygEIkqHLAQiKo8sBCPWYzQEIhaDNAQji0M4BCLPTzgEI19TOAQjy1c4BCJLYzgEIwNjOAQjM2M4BGM7VzgE=",
        }
        cookies = {"SOCS": "CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg"}
        files = {"encoded_image": ("screenshot.png", imagebinary, "image/png")}
        res = self.proxysession.post(
            url, files=files, params=params, headers=headers, cookies=cookies
        )
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
