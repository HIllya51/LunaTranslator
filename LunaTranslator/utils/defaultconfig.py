import json

defaultglobalconfig='''
{
    "position": [
        432,
        613
    ],
    "fixedheight": false,
    "width": 768.8,
    "autorun": true,
    "transparent": 82,
    "fontsize": 17.699999999999996,
    "fonttype": "思源黑体 CN Medium",
    "issolid": false,
    "isshowrawtext": true,
    "rawtextcolor": "#000000",
    "backcolor": "#7a8b8a",
    "isshowhira": false,
    "locktools": true,
    "showfanyisource": true,
    "autoread": false,
    "reader": {
        "qq": false,
        "guge": true,
        "windows": true
    },
    "windowstts": {
        "voice": "TTS_MS_EN-US_ZIRA_11.0",
        "rate": 1.0,
        "volume": 100.0
    },
    "sourcestatus": {
        "copy": true,
        "ocr": false,
        "textractor": false,
        "textractor_pipe": false
    },
    "ocr": {
        "local": {
            "use": true,
            "name": "本地OCR"
        },
        "baiduocr": {
            "use": false,
            "name": "baiduOCR",
            "argsfile": "./userconfig/baiduocr.json"
        },
        "ocrspace": {
            "use": false,
            "name": "ocrspace",
            "argsfile": "./userconfig/ocrspace.json"
        },
        "docsumo": {
            "use": false,
            "name": "docsumo",
            "argsfile": "./userconfig/docsumo.json"
        }
    },
    "fanyi": {
        "baidu": {
            "use": true,
            "color": "#ff65db",
            "name": "百度"
        },
        "bing": {
            "use": false,
            "color": "#000ff0",
            "name": "必应"
        },
        "google": {
            "use": false,
            "color": "#ff0000",
            "name": "谷歌"
        },
        "ali": {
            "use": false,
            "color": "#0000ff",
            "name": "阿里"
        },
        "youdao": {
            "use": false,
            "color": "#0ff000",
            "name": "有道"
        },
        "youdao2": {
            "use": false,
            "color": "#0ff000",
            "name": "有道2"
        },
        "google2": {
            "use": false,
            "color": "#95a5ff",
            "name": "谷歌2"
        },
        "sougou": {
            "use": false,
            "color": "#0ff000",
            "name": "搜狗"
        },
        "caiyun": {
            "use": false,
            "color": "#0ff000",
            "name": "彩云"
        },
        "deepl": {
            "use": false,
            "color": "#0ff000",
            "name": "deepl"
        },
        "jb7": {
            "use": true,
            "color": "#1839f0",
            "name": "Jbeijing7",
            "argsfile": "./userconfig/jbj7.json"
        },
        "kingsoft": {
            "use": true,
            "color": "#1839f0",
            "name": "金山快译",
            "argsfile": "./userconfig/ks.json"
        },
        "dreye": {
            "use": true,
            "color": "#1839f0",
            "name": "快译通",
            "argsfile": "./userconfig/dreye.json"
        },
        "sougou2": {
            "use": false,
            "color": "#0ff000",
            "name": "搜狗2"
        },
        "youdao3": {
            "use": false,
            "color": "#0ff000",
            "name": "有道3"
        },
        "selfbuild": {
            "use": false,
            "color": "#0ff000",
            "name": "自建"
        },
        "tencent": {
            "use": false,
            "color": "#0ff000",
            "name": "TX"
        },
        "ifly": {
            "use": false,
            "color": "#0ff000",
            "name": "ifly"
        },
        "iciba": {
            "use": false,
            "color": "#0ff000",
            "name": "iciba"
        },
        "baiduapi": {
            "use": false,
            "color": "#0ff000",
            "name": "百度api",
            "argsfile": "./userconfig/baiduapi.json"
        },
        "tencentapi": {
            "use": false,
            "color": "#0ff000",
            "name": "腾讯api",
            "argsfile": "./userconfig/txapi.json"
        },
        "byte": {
            "use": false,
            "color": "#0ff000",
            "name": "byte"
        },
        "qqimt": {
            "use": false,
            "color": "#0ff000",
            "name": "qqimt"
        },
        "xiaoniu": {
            "use": false,
            "color": "#0ff000",
            "name": "小牛",
            "argsfile": "./userconfig/xiaoniuapi.json"
        }
    },
    "minifollow": true,
    "movefollow": true,
    "autostarthook": true,
    "translatortimeout": 5,
    "minlength": 0,
    "maxlength": 150,
    "fanjian": 0,
    "rotation": 0,
    "srclang": 0
}
'''

defaultpost='''
{
    "_1": {
        "use": true,
        "name": "去除花括号{}"
    },
    "_2": {
        "use": true,
        "name": "去除重复字符(0为自动删除,1为不删除)",
        "args": {
            "重复次数": 1
        }
    },
    "_3": {
        "use": true,
        "name": "去除重复行"
    },
    "_4": {
        "use": true,
        "name": "过滤HTML标签"
    },
    "_6": {
        "use": true,
        "name": "过滤换行符"
    },
    "_5": {
        "use": true,
        "name": "过滤指定内容，每行一个",
        "args": {
            "过滤内容": [
                " "
            ]
        }
    }
}
'''

defaulterrorfix='''
{
    "use": true,
    "dict": {}
}
'''

defaultnoun='''
{
    "use": true,
    "dict": {}
}
'''

defaultglobalconfig=json.loads(defaultglobalconfig)
defaultpost=json.loads(defaultpost)
defaulterrorfix=json.loads(defaulterrorfix)
defaultnoun=json.loads(defaultnoun)