from qtsymbols import *
import requests, base64, json
from ocrengines.baseocrclass import baseocr, OCRResult
from urllib.parse import urlparse, parse_qs
from myutils.utils import qimage2binary

# https://github.com/AuroraWright/owocr/blob/master/owocr/ocr.py#L370


class Bing:

    def __init__(self, session: requests.Session):
        self.requests_session = session

    def __call__(self, img_bytes: bytes, w: int, h: int):

        host = "www.bing.com"
        upload_url = "https://www.bing.com/images/search?view=detailv2&iss=sbiupload"
        upload_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "ja-JP;q=0.6,ja;q=0.5",
            "cache-control": "max-age=0",
            "origin": "https://www.bing.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        }
        files = {
            "imgurl": (None, ""),
            "cbir": (None, "sbi"),
            "imageBin": (None, base64.b64encode(img_bytes).decode("utf-8")),
        }
        for _ in range(2):
            res = self.requests_session.post(
                upload_url,
                headers=upload_headers,
                files=files,
                allow_redirects=False,
            )
            if res.status_code != 302:
                raise Exception("Unknown error!")
            redirect_url: str = res.headers.get("Location")
            if not redirect_url:
                raise Exception("Error getting redirect URL!")
            if not redirect_url.startswith("https://"):
                break
            host = urlparse(redirect_url).netloc
            upload_url = redirect_url
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)

        image_insights_token = query_params.get("insightsToken")
        if not image_insights_token:
            raise Exception("Error getting token!")
        image_insights_token = image_insights_token[0]

        api_url = "https://{}/images/api/custom/knowledge".format(host)
        api_headers = {
            "accept": "*/*",
            "accept-language": "ja-JP;q=0.6,ja;q=0.5",
            "origin": "https://www.bing.com",
            "referer": "https://www.bing.com/images/search?view=detailV2&insightstoken={}".format(
                image_insights_token
            ),
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        }
        api_data_json = {
            "imageInfo": {"imageInsightsToken": image_insights_token, "source": "Url"},
            "knowledgeRequest": {"invokedSkills": ["OCR"], "index": 1},
        }
        files = {
            "knowledgeRequest": (None, json.dumps(api_data_json), "application/json")
        }

        res = self.requests_session.post(api_url, headers=api_headers, files=files)

        data = res.json()
        text_tag = None
        for tag in data["tags"]:
            if tag.get("displayName") == "##TextRecognition":
                text_tag = tag
                break
        if not text_tag:
            return

        text_action = None
        for action in text_tag["actions"]:
            if action.get("_type") == "ImageKnowledge/TextRecognitionAction":
                text_action = action
                break
        if not text_action:
            return

        regions = text_action["data"].get("regions", [])
        texts = []
        boxs = []
        res = ""
        for region in regions:
            for line in region.get("lines", []):
                texts.append(line["text"])
                boundingBox = line["boundingBox"]
                topLeft = boundingBox["topLeft"]
                topRight = boundingBox["topRight"]
                bottomRight = boundingBox["bottomRight"]
                bottomLeft = boundingBox["bottomLeft"]
                boxs.append(
                    [
                        topLeft["x"] * w,
                        topLeft["y"] * h,
                        topRight["x"] * w,
                        topRight["y"] * h,
                        bottomRight["x"] * w,
                        bottomRight["y"] * h,
                        bottomLeft["x"] * w,
                        bottomLeft["y"] * h,
                    ]
                )

        return OCRResult(boxs=boxs, texts=texts)


class OCR(baseocr):

    required_image_format = QImage

    def ocr(self, data: QImage):
        return Bing(self.proxysession)(
            qimage2binary(data, "PNG"), data.width(), data.height()
        )
