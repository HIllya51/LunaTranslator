import json

defaultglobalconfig = {'position': [432, 613], 'fixedheight': False, 'width': 768.8, 'autorun': True, 'transparent': 82, 'fontsize': 17.699999999999996, 'fonttype': '思源黑体 CN Medium', 'issolid': False, 'iskongxin': True, 'isshowrawtext': True, 'rawtextcolor': '#000000', 'backcolor': '#7a8b8a', 'isshowhira': False, 'locktools': True, 'showfanyisource': True, 'autoread': False, 'extractalltext': False, 'reader': {'qq': False, 'guge': True, 'windows': True}, 'LocaleEmulator': '', 'verticalocr': False, 'outputtopasteboard': False, 'windowstts': {'voice': 'TTS_MS_EN-US_ZIRA_11.0', 'rate': 1.0, 'volume': 100.0}, 'sourcestatus': {'copy': True, 'ocr': False, 'textractor': False, 'textractor_pipe': False}, 'ocr': {'local': {'use': True, 'name': '本地OCR'}, 'baiduocr': {'use': False, 'name': 'baiduOCR', 'argsfile': './userconfig/baiduocr.json'}, 'ocrspace': {'use': False, 'name': 'ocrspace', 'argsfile': './userconfig/ocrspace.json'}, 'docsumo': {'use': False, 'name': 'docsumo', 'argsfile': './userconfig/docsumo.json'},
 'youdaocr': {'use': False, 'name': 'youdaocr'}, 'youdaocrtrans': {'use': False, 'name': 'youdao图片翻译'}
 },
 'fanyi': {'baidu': {'use': True, 'color': '#ff65db', 'name': '百度'}, 'bing': {'use': False, 'color': '#000ff0', 'name': '必应'}, 'google': {'use': False, 'color': '#ff0000', 'name': '谷歌'}, 'ali': {'use': False, 'color': '#0000ff', 'name': '阿里'}, 'youdao': {'use': False, 'color': '#0ff000', 'name': '有道'}, 'youdao2': {'use': False, 'color': '#0ff000', 'name': '有道2'}, 'google2': {'use': False, 'color': '#95a5ff', 'name': '谷歌2'}, 'sougou': {
    'use': False, 'color': '#0ff000', 'name': '搜狗'}, 'caiyun': {'use': False, 'color': '#0ff000', 'name': '彩云'},'deepl': {'use': False, 'color': '#0ff000', 'name': 'deepl'}, 'jb7': {'use': True, 'color': '#1839f0', 'name': 'Jbeijing7', 'argsfile': './userconfig/jbj7.json'}, 'kingsoft': {'use': True, 'color': '#1839f0', 'name': '金山快译', 'argsfile': './userconfig/ks.json'}, 'dreye': {'use': True, 'color': '#1839f0', 'name': '快译通', 'argsfile': './userconfig/dreye.json'}, 'sougou2': {'use': False, 'color': '#0ff000', 'name': '搜狗2'}, 'youdao3': {'use': False, 'color': '#0ff000', 'name': '有道3'}, 'youdao4': {'use': False, 'color': '#0ff000', 'name': '有道4'}, 'youdao5': {'use': False, 'color': '#0ff000', 'name': '有道5'}, 'selfbuild': {'use': False, 'color': '#0ff000', 'name': '自建'}, 'tencent': {'use': False, 'color': '#0ff000', 'name': 'TX'}, 'ifly': {'use': False, 'color': '#0ff000', 'name': 'ifly'}, 'iciba': {'use': False, 'color': '#0ff000', 'name': 'iciba'}, 'baiduapi': {'use': False, 'color': '#0ff000', 'name': '百度api', 'argsfile': './userconfig/baiduapi.json'}, 'tencentapi': {'use': False, 'color': '#0ff000', 'name': '腾讯api', 'argsfile': './userconfig/txapi.json'}, 'byte': {'use': False, 'color': '#0ff000', 'name': 'byte'}, 'qqimt': {'use': False, 'color': '#0ff000', 'name': 'qqimt'}, 'xiaoniu': {'use': False, 'color': '#0ff000', 'name': '小牛api', 'argsfile': './userconfig/xiaoniuapi.json'},
    'huoshan': {'use': False, 'color': '#0ff000', 'name': 'huoshan' },
    'yeekit': {'use': False, 'color': '#0ff000', 'name': 'yeekit' }, 'caiyunapi': {'use': False, 'color': '#0ff000', 'name': '彩云api', 'argsfile': './userconfig/caiyunapi.json'}
    }, 'minifollow': True, 'movefollow': True, 'autostarthook': True, 'translatortimeout': 5, 'minlength': 0, 'maxlength': 150, 'fanjian': 0, 'rotation': 0, 'srclang': 0}

defaultpost = {'_1': {'use': True, 'name': '去除花括号{}'}, '_2': {'use': True, 'name': '去除重复字符(0为自动删除,1为不删除)', 'args': {'重复次数': 1}}, '_3': {'use': True, 'name': '去除重复行'}, '_4': {
    'use': True, 'name': '过滤HTML标签'}, '_6': {'use': True, 'name': '过滤换行符'}, '_5': {'use': True, 'name': '过滤指定内容每行一个', 'args': {'过滤内容': [' ']}}}

defaulterrorfix = {
    "use": True,
    "dict": {}
}


defaultnoun = {
    "use": True,
    "dict": {}
}
