import re, uuid
from cishu.cishubase import cishubase

style = r"""
<style>
    .cloud-result p{
    --color-grey: #dcdfe6;
    --color-grey-secondary: #8b8787;
    --color-grey-third: #acacac;
    --color-grey-fourth: #e4e4e4;
    --color-grey-fifth: #d8d8d8;
    --color-grey-sixth: #d1d1d1;
    --color-black-primary: #606266;
    --color-primary: #ff5252;
    --bg-primary: #ff3a3a;
    --border-bar: #e7e7e7;
    --color-blue-description: #46a3f4;
    --bg-switch-core-active: #ff5252;
    --bg-scrollbar: hsla(0,0%,67%,.5);
    --input-split: #ececec;
    --filter-icon: invert(0);
    --content-color: #3a3a3a;
    --color: #3d454c;
    --color-desc: #8b8787;
    --color-secondary: #5a5e66;
    --bg: #f8f8f8;
    --bg-secondary: #fff;
    --bg-third: #f1f1f1;
    --bg-fourth: #fff;
    --bg-fifth: #fff5f5;
    --bg-sixth: #d8d8d8;
    --bg-seventh: #f8f8f8;
    --bg-icon: #e4e4e4;
    --bg-hover-primary: #ff3a3a;
    --border-color: #dcdfe6;
    --border-color-primary: #ffcbcb;
    --border-color-secondary: #ffb7b7;
    --border-color-third: #ececec;
    --btn-border: #ffcbcb;
    --btn-primary-secondary: #ffd8d8;
    --btn-color: #ff3a3a;
    --btn-bg: #fff5f5;
    --folder: #ffe88c;
    --border: #ececec;
    --hr: #d8d8d8;
    --bg-input: #f9f9f9;
    --border-input: #dfdfdf;
    --hover-color: rgba(0,0,0,.04);
    --border-btn-basic: #ff3a3a;
    --color-slider: #ececec;
    --bg-tag: rgba(0,0,0,.04);
    --bg-card-hover: #fff;
    --bg-image: #ececec;
    --search-input-border: #3b3b3b;
    --boxshadow-search: #ececec;
    --bg-search-input: #fff;
    --bg-setting-card: #fff;
    --bg-slider: #f8f8f8;
    --bg-slider-active: #fff;
    --bg-switch: #f8f8f8;
    --bg-switch-core: #ececec;
    --border-tag: #acacac;
    --bg-article-translation: rgba(0,0,0,.02);
    --content-hover-bg: #ffcbcb;
    --bg-radio: #ff5252;
    --radio-color: #fff;
    --bg-chunk-yellow: #fae6b8;
    --bg-chunk-blue: #ececec;
    --bg-chunk-gray: #ececec;
    --bg-chunk-orange: #fae6b8;
    --border-chunk-color-gray: #ccc;
    --border-chunk-color-orange: #ffc84a;
    --content-color-analysis: #3a3a3a;
    --color-gray: #8b8787;
    --bg-radio-second: #1c1c1e;
    font-family: -apple-system,PingFangSC-Regular,AlibabaPuHuiTi,Microsoft Yahei,黑体,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Open Sans,Helvetica Neue,sans-serif;
    line-height: 1.4;
    text-align: justify;
    word-break: break-all;
    color: var(--color);
    font-size: 14px;
    white-space: normal;
    box-sizing: border-box;
    margin: 0 0 6px;
    }
    .cloud-result .type{
    --color-grey: #dcdfe6;
    --color-grey-secondary: #8b8787;
    --color-grey-third: #acacac;
    --color-grey-fourth: #e4e4e4;
    --color-grey-fifth: #d8d8d8;
    --color-grey-sixth: #d1d1d1;
    --color-black-primary: #606266;
    --color-primary: #ff5252;
    --bg-primary: #ff3a3a;
    --border-bar: #e7e7e7;
    --color-blue-description: #46a3f4;
    --bg-switch-core-active: #ff5252;
    --bg-scrollbar: hsla(0,0%,67%,.5);
    --input-split: #ececec;
    --filter-icon: invert(0);
    --content-color: #3a3a3a;
    --color: #3d454c;
    --color-desc: #8b8787;
    --color-secondary: #5a5e66;
    --bg: #f8f8f8;
    --bg-secondary: #fff;
    --bg-third: #f1f1f1;
    --bg-fourth: #fff;
    --bg-fifth: #fff5f5;
    --bg-sixth: #d8d8d8;
    --bg-seventh: #f8f8f8;
    --bg-icon: #e4e4e4;
    --bg-hover-primary: #ff3a3a;
    --border-color: #dcdfe6;
    --border-color-primary: #ffcbcb;
    --border-color-secondary: #ffb7b7;
    --border-color-third: #ececec;
    --btn-border: #ffcbcb;
    --btn-primary-secondary: #ffd8d8;
    --btn-color: #ff3a3a;
    --btn-bg: #fff5f5;
    --folder: #ffe88c;
    --border: #ececec;
    --hr: #d8d8d8;
    --bg-input: #f9f9f9;
    --border-input: #dfdfdf;
    --hover-color: rgba(0,0,0,.04);
    --border-btn-basic: #ff3a3a;
    --color-slider: #ececec;
    --bg-tag: rgba(0,0,0,.04);
    --bg-card-hover: #fff;
    --bg-image: #ececec;
    --search-input-border: #3b3b3b;
    --boxshadow-search: #ececec;
    --bg-search-input: #fff;
    --bg-setting-card: #fff;
    --bg-slider: #f8f8f8;
    --bg-slider-active: #fff;
    --bg-switch: #f8f8f8;
    --bg-switch-core: #ececec;
    --border-tag: #acacac;
    --bg-article-translation: rgba(0,0,0,.02);
    --content-hover-bg: #ffcbcb;
    --bg-radio: #ff5252;
    --radio-color: #fff;
    --bg-chunk-yellow: #fae6b8;
    --bg-chunk-blue: #ececec;
    --bg-chunk-gray: #ececec;
    --bg-chunk-orange: #fae6b8;
    --border-chunk-color-gray: #ccc;
    --border-chunk-color-orange: #ffc84a;
    --content-color-analysis: #3a3a3a;
    --color-gray: #8b8787;
    --bg-radio-second: #1c1c1e;
    font-family: -apple-system,PingFangSC-Regular,AlibabaPuHuiTi,Microsoft Yahei,黑体,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Open Sans,Helvetica Neue,sans-serif;
    line-height: 1.4;
    text-align: justify;
    word-break: break-all;
    color: var(--color);
    font-size: 14px;
    white-space: normal;
    box-sizing: border-box;
    margin: 0 0 6px;
    }
    .cloud-result .detail{
    --color-grey: #dcdfe6;
    --color-grey-secondary: #8b8787;
    --color-grey-third: #acacac;
    --color-grey-fourth: #e4e4e4;
    --color-grey-fifth: #d8d8d8;
    --color-grey-sixth: #d1d1d1;
    --color-black-primary: #606266;
    --color-primary: #ff5252;
    --bg-primary: #ff3a3a;
    --border-bar: #e7e7e7;
    --color-blue-description: #46a3f4;
    --bg-switch-core-active: #ff5252;
    --bg-scrollbar: hsla(0,0%,67%,.5);
    --input-split: #ececec;
    --filter-icon: invert(0);
    --content-color: #3a3a3a;
    --color: #3d454c;
    --color-desc: #8b8787;
    --color-secondary: #5a5e66;
    --bg: #f8f8f8;
    --bg-secondary: #fff;
    --bg-third: #f1f1f1;
    --bg-fourth: #fff;
    --bg-fifth: #fff5f5;
    --bg-sixth: #d8d8d8;
    --bg-seventh: #f8f8f8;
    --bg-icon: #e4e4e4;
    --bg-hover-primary: #ff3a3a;
    --border-color: #dcdfe6;
    --border-color-primary: #ffcbcb;
    --border-color-secondary: #ffb7b7;
    --border-color-third: #ececec;
    --btn-border: #ffcbcb;
    --btn-primary-secondary: #ffd8d8;
    --btn-color: #ff3a3a;
    --btn-bg: #fff5f5;
    --folder: #ffe88c;
    --border: #ececec;
    --hr: #d8d8d8;
    --bg-input: #f9f9f9;
    --border-input: #dfdfdf;
    --hover-color: rgba(0,0,0,.04);
    --border-btn-basic: #ff3a3a;
    --color-slider: #ececec;
    --bg-tag: rgba(0,0,0,.04);
    --bg-card-hover: #fff;
    --bg-image: #ececec;
    --search-input-border: #3b3b3b;
    --boxshadow-search: #ececec;
    --bg-search-input: #fff;
    --bg-setting-card: #fff;
    --bg-slider: #f8f8f8;
    --bg-slider-active: #fff;
    --bg-switch: #f8f8f8;
    --bg-switch-core: #ececec;
    --border-tag: #acacac;
    --bg-article-translation: rgba(0,0,0,.02);
    --content-hover-bg: #ffcbcb;
    --bg-radio: #ff5252;
    --radio-color: #fff;
    --bg-chunk-yellow: #fae6b8;
    --bg-chunk-blue: #ececec;
    --bg-chunk-gray: #ececec;
    --bg-chunk-orange: #fae6b8;
    --border-chunk-color-gray: #ccc;
    --border-chunk-color-orange: #ffc84a;
    --content-color-analysis: #3a3a3a;
    --color-gray: #8b8787;
    --bg-radio-second: #1c1c1e;
    font-family: -apple-system,PingFangSC-Regular,AlibabaPuHuiTi,Microsoft Yahei,黑体,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Open Sans,Helvetica Neue,sans-serif;
    line-height: 1.4;
    text-align: justify;
    word-break: break-all;
    color: var(--color);
    font-size: 14px;
    white-space: normal;
    box-sizing: border-box;
    margin: 0;
    }
    .cloud-result .spell{
    --color-grey: #dcdfe6;
    --color-grey-secondary: #8b8787;
    --color-grey-third: #acacac;
    --color-grey-fourth: #e4e4e4;
    --color-grey-fifth: #d8d8d8;
    --color-grey-sixth: #d1d1d1;
    --color-black-primary: #606266;
    --color-primary: #ff5252;
    --bg-primary: #ff3a3a;
    --border-bar: #e7e7e7;
    --color-blue-description: #46a3f4;
    --bg-switch-core-active: #ff5252;
    --bg-scrollbar: hsla(0,0%,67%,.5);
    --input-split: #ececec;
    --filter-icon: invert(0);
    --content-color: #3a3a3a;
    --color: #3d454c;
    --color-desc: #8b8787;
    --color-secondary: #5a5e66;
    --bg: #f8f8f8;
    --bg-secondary: #fff;
    --bg-third: #f1f1f1;
    --bg-fourth: #fff;
    --bg-fifth: #fff5f5;
    --bg-sixth: #d8d8d8;
    --bg-seventh: #f8f8f8;
    --bg-icon: #e4e4e4;
    --bg-hover-primary: #ff3a3a;
    --border-color: #dcdfe6;
    --border-color-primary: #ffcbcb;
    --border-color-secondary: #ffb7b7;
    --border-color-third: #ececec;
    --btn-border: #ffcbcb;
    --btn-primary-secondary: #ffd8d8;
    --btn-color: #ff3a3a;
    --btn-bg: #fff5f5;
    --folder: #ffe88c;
    --border: #ececec;
    --hr: #d8d8d8;
    --bg-input: #f9f9f9;
    --border-input: #dfdfdf;
    --hover-color: rgba(0,0,0,.04);
    --border-btn-basic: #ff3a3a;
    --color-slider: #ececec;
    --bg-tag: rgba(0,0,0,.04);
    --bg-card-hover: #fff;
    --bg-image: #ececec;
    --search-input-border: #3b3b3b;
    --boxshadow-search: #ececec;
    --bg-search-input: #fff;
    --bg-setting-card: #fff;
    --bg-slider: #f8f8f8;
    --bg-slider-active: #fff;
    --bg-switch: #f8f8f8;
    --bg-switch-core: #ececec;
    --border-tag: #acacac;
    --bg-article-translation: rgba(0,0,0,.02);
    --content-hover-bg: #ffcbcb;
    --bg-radio: #ff5252;
    --radio-color: #fff;
    --bg-chunk-yellow: #fae6b8;
    --bg-chunk-blue: #ececec;
    --bg-chunk-gray: #ececec;
    --bg-chunk-orange: #fae6b8;
    --border-chunk-color-gray: #ccc;
    --border-chunk-color-orange: #ffc84a;
    --content-color-analysis: #3a3a3a;
    --color-gray: #8b8787;
    --bg-radio-second: #1c1c1e;
    font-family: -apple-system,PingFangSC-Regular,AlibabaPuHuiTi,Microsoft Yahei,黑体,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Open Sans,Helvetica Neue,sans-serif;
    line-height: 1.4;
    text-align: justify;
    word-break: break-all;
    color: var(--color);
    white-space: normal;
    box-sizing: border-box;
    margin: 0;
    align-items: center;
    display: flex;
    flex-direction: row;
    margin-bottom: 12px;
    font-size: 18px;
    }
    .cloud-result .spell span{
    --color-grey: #dcdfe6;
    --color-grey-secondary: #8b8787;
    --color-grey-third: #acacac;
    --color-grey-fourth: #e4e4e4;
    --color-grey-fifth: #d8d8d8;
    --color-grey-sixth: #d1d1d1;
    --color-black-primary: #606266;
    --color-primary: #ff5252;
    --bg-primary: #ff3a3a;
    --border-bar: #e7e7e7;
    --color-blue-description: #46a3f4;
    --bg-switch-core-active: #ff5252;
    --bg-scrollbar: hsla(0,0%,67%,.5);
    --input-split: #ececec;
    --filter-icon: invert(0);
    --content-color: #3a3a3a;
    --color: #3d454c;
    --color-desc: #8b8787;
    --color-secondary: #5a5e66;
    --bg: #f8f8f8;
    --bg-secondary: #fff;
    --bg-third: #f1f1f1;
    --bg-fourth: #fff;
    --bg-fifth: #fff5f5;
    --bg-sixth: #d8d8d8;
    --bg-seventh: #f8f8f8;
    --bg-icon: #e4e4e4;
    --bg-hover-primary: #ff3a3a;
    --border-color: #dcdfe6;
    --border-color-primary: #ffcbcb;
    --border-color-secondary: #ffb7b7;
    --border-color-third: #ececec;
    --btn-border: #ffcbcb;
    --btn-primary-secondary: #ffd8d8;
    --btn-color: #ff3a3a;
    --btn-bg: #fff5f5;
    --folder: #ffe88c;
    --border: #ececec;
    --hr: #d8d8d8;
    --bg-input: #f9f9f9;
    --border-input: #dfdfdf;
    --hover-color: rgba(0,0,0,.04);
    --border-btn-basic: #ff3a3a;
    --color-slider: #ececec;
    --bg-tag: rgba(0,0,0,.04);
    --bg-card-hover: #fff;
    --bg-image: #ececec;
    --search-input-border: #3b3b3b;
    --boxshadow-search: #ececec;
    --bg-search-input: #fff;
    --bg-setting-card: #fff;
    --bg-slider: #f8f8f8;
    --bg-slider-active: #fff;
    --bg-switch: #f8f8f8;
    --bg-switch-core: #ececec;
    --border-tag: #acacac;
    --bg-article-translation: rgba(0,0,0,.02);
    --content-hover-bg: #ffcbcb;
    --bg-radio: #ff5252;
    --radio-color: #fff;
    --bg-chunk-yellow: #fae6b8;
    --bg-chunk-blue: #ececec;
    --bg-chunk-gray: #ececec;
    --bg-chunk-orange: #fae6b8;
    --border-chunk-color-gray: #ccc;
    --border-chunk-color-orange: #ffc84a;
    --content-color-analysis: #3a3a3a;
    --color-gray: #8b8787;
    --bg-radio-second: #1c1c1e;
    font-family: -apple-system,PingFangSC-Regular,AlibabaPuHuiTi,Microsoft Yahei,黑体,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Open Sans,Helvetica Neue,sans-serif;
    text-align: justify;
    word-break: break-all;
    color: var(--color);
    white-space: normal;
    font-size: 18px;
    box-sizing: border-box;
    margin: 0;
    line-height: 24px;
    vertical-align: middle;
    }
    .cloud-result{
    --color-grey: #dcdfe6;
    --color-grey-secondary: #8b8787;
    --color-grey-third: #acacac;
    --color-grey-fourth: #e4e4e4;
    --color-grey-fifth: #d8d8d8;
    --color-grey-sixth: #d1d1d1;
    --color-black-primary: #606266;
    --color-primary: #ff5252;
    --bg-primary: #ff3a3a;
    --border-bar: #e7e7e7;
    --color-blue-description: #46a3f4;
    --bg-switch-core-active: #ff5252;
    --bg-scrollbar: hsla(0,0%,67%,.5);
    --input-split: #ececec;
    --filter-icon: invert(0);
    --content-color: #3a3a3a;
    --color: #3d454c;
    --color-desc: #8b8787;
    --color-secondary: #5a5e66;
    --bg: #f8f8f8;
    --bg-secondary: #fff;
    --bg-third: #f1f1f1;
    --bg-fourth: #fff;
    --bg-fifth: #fff5f5;
    --bg-sixth: #d8d8d8;
    --bg-seventh: #f8f8f8;
    --bg-icon: #e4e4e4;
    --bg-hover-primary: #ff3a3a;
    --border-color: #dcdfe6;
    --border-color-primary: #ffcbcb;
    --border-color-secondary: #ffb7b7;
    --border-color-third: #ececec;
    --btn-border: #ffcbcb;
    --btn-primary-secondary: #ffd8d8;
    --btn-color: #ff3a3a;
    --btn-bg: #fff5f5;
    --folder: #ffe88c;
    --border: #ececec;
    --hr: #d8d8d8;
    --bg-input: #f9f9f9;
    --border-input: #dfdfdf;
    --hover-color: rgba(0,0,0,.04);
    --border-btn-basic: #ff3a3a;
    --color-slider: #ececec;
    --bg-tag: rgba(0,0,0,.04);
    --bg-card-hover: #fff;
    --bg-image: #ececec;
    --search-input-border: #3b3b3b;
    --boxshadow-search: #ececec;
    --bg-search-input: #fff;
    --bg-setting-card: #fff;
    --bg-slider: #f8f8f8;
    --bg-slider-active: #fff;
    --bg-switch: #f8f8f8;
    --bg-switch-core: #ececec;
    --border-tag: #acacac;
    --bg-article-translation: rgba(0,0,0,.02);
    --content-hover-bg: #ffcbcb;
    --bg-radio: #ff5252;
    --radio-color: #fff;
    --bg-chunk-yellow: #fae6b8;
    --bg-chunk-blue: #ececec;
    --bg-chunk-gray: #ececec;
    --bg-chunk-orange: #fae6b8;
    --border-chunk-color-gray: #ccc;
    --border-chunk-color-orange: #ffc84a;
    --content-color-analysis: #3a3a3a;
    --color-gray: #8b8787;
    --bg-radio-second: #1c1c1e;
    font-family: -apple-system,PingFangSC-Regular,AlibabaPuHuiTi,Microsoft Yahei,黑体,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Open Sans,Helvetica Neue,sans-serif;
    line-height: 1.4;
    text-align: justify;
    word-break: break-all;
    color: var(--color);
    font-size: 14px;
    white-space: normal;
    box-sizing: border-box;
    margin: 0;
    }

</style>
"""


class mojidict(cishubase):
    def mojiclicksearch(self, word):

        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7,ru;q=0.6",
            "origin": "https://www.mojidict.com",
            "priority": "u=1, i",
            "referer": "https://www.mojidict.com/",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"
        }
        data = {
            "searchText": word,
            "langEnv": "zh-CN_ja",
            "_ClientVersion": "js3.4.1",
            "_ApplicationId": "E62VyFVLMiW7kvbtVq3p",
            "g_os": "PCWeb",
            "g_ver": "v4.8.8.20240829",
            "_InstallationId": "563b6bd3-e514-46fb-8557-d6138311a06c",
        }

        response = self.proxysession.post(
            "https://api.mojidict.com/parse/functions/word-clickSearchV2",
            headers=headers,
            json=data,
        )

        result = response.json()["result"]["result"]
        word = result["word"]

        subdetails = result["subdetails"]
        collect = []
        relaid = []

        for subdetail in subdetails:
            title = subdetail["title"]
            # print(title,subdetail)

            good = False
            for i in range(len(relaid)):
                if relaid[i] == subdetail["relaId"]:
                    if subdetail["lang"] == "zh-CN":
                        collect[i] = title + collect[i]
                    elif subdetail["lang"] == "ja":
                        title = "(" + title + ")"
                        collect[i] = collect[i] + title
                    good = True
            if not good:
                collect.append(title)
                relaid.append(subdetail["relaId"])
        # print('\n'.join(collect))
        excerpt = word[0]["excerpt"]
        accent = word[0]["accent"]
        spell = word[0]["spell"]
        pron = word[0]["pron"]

        spell = "<span>{}｜{}{}</span>".format(spell, pron, accent)
        spell = '<div class="spell" style="font-size: 18px;">{}</div>'.format(spell)
        _type = re.match("\\[(.*?)\\]", excerpt).groups()[0]
        _type = '<p class="type">{}</p>'.format(_type)
        klass = "luna" + str(uuid.uuid4())
        for i in range(len(collect)):
            collect[i] = "<p>{}. {}</p>".format(i + 1, collect[i])
        detail = """<div class="detail">{}{}</div>""".format(_type, "".join(collect))
        result = '<div class="{}">{}{}</div>'.format(klass, spell, detail)
        result += style.replace("cloud-result", klass)
        return result

    def mojizonghe(self, word):
        response = self.proxysession.post(
            "https://api.mojidict.com/parse/functions/union-api",
            json={
                "functions": [
                    {
                        "name": "search-all",
                        "params": {
                            "text": word,
                            "types": [
                                102,
                                106,
                                103,
                            ],
                        },
                    },
                ],
                "_ClientVersion": "js3.4.1",
                "_ApplicationId": "E62VyFVLMiW7kvbtVq3p",
                "g_os": "PCWeb",
                "g_ver": "v4.8.8.20240829",
                "_InstallationId": "563b6bd3-e514-46fb-8557-d6138311a06c",
            },
            headers={
                "accept": "*/*",
                "accept-language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7,ru;q=0.6",
                "content-type": "text/plain",
                "origin": "https://www.mojidict.com",
                "priority": "u=1, i",
                "referer": "https://www.mojidict.com/",
                "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
            },
        )

        result = ""
        for i in response.json()["result"]["results"]["search-all"]["result"]["word"][
            "searchResult"
        ]:
            result += "{}<br>{}<br><br>".format(i["title"], i["excerpt"])

        return result

    def search(self, word):

        result = ""
        try:
            result += self.mojiclicksearch(word)
            result += "<hr>"
        except:
            pass
        try:
            result += self.mojizonghe(word)
        except:
            pass
        if result:
            return '<div style="padding:10px">{}</div>'.format(result)
