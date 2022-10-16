 
defaultglobalconfig = {'position': [432, 613], 'fixedheight': False, 'width': 768.8, 'autorun': True, 'transparent': 82, 'fontsize': 17.699999999999996, 'fonttype': '思源黑体 CN Heavy',  'miaobianwidth':1,'miaobiancolor':'#eeeeee',
 'iskongxin': True, 'isshowrawtext': True, 'rawtextcolor': '#000000', 'backcolor': '#7a8b8a', 'isshowhira': False, 'locktools': True, 'showfanyisource': True, 'autoread': False, 'extractalltext': False, 'reader': {'azuretts':{'use':False,'voice':''}, 'huoshantts':{'use':False,'voice':''}, 'windowstts': {'use':False,'voice':''}}, 'LocaleEmulator': '', 'verticalocr': False, 'outputtopasteboard': False, 'ttscommon': { 'rate': 1.0, 'volume': 100.0},

 'sourcestatus': {'copy': True, 'ocr': False, 'textractor': False, 'textractor_pipe': False}, 'ocr': {'local': {'use': True, 'name': '本地OCR'}, 'baiduocr': {'use': False, 'name': 'baiduOCR', 'argsfile': './userconfig/baiduocr.json'}, 'ocrspace': {'use': False, 'name': 'ocrspace', 'argsfile': './userconfig/ocrspace.json'}, 'docsumo': {'use': False, 'name': 'docsumo', 'argsfile': './userconfig/docsumo.json'},
 'youdaocr': {'use': False, 'name': 'youdaocr'}, 'youdaocrtrans': {'use': False, 'name': 'youdao图片翻译'}
 },
 'fanyi': {
    'baidu': {'use': True, 'color': '#ff65db', 'name': '百度'}, 'bing': {'use': False, 'color': '#000ff0', 'name': '必应'}, 
    # 'google': {'use': False, 'color': '#ff0000', 'name': '谷歌'}, 
    'ali': {'use': False, 'color': '#0000ff', 'name': '阿里'}, 'youdao': {'use': False, 'color': '#0ff000', 'name': '有道'}, 'youdao2': {'use': False, 'color': '#0ff000', 'name': '有道2'},
    #  'google2': {'use': False, 'color': '#95a5ff', 'name': '谷歌2'},
      'sougou': {
    'use': False, 'color': '#0ff000', 'name': '搜狗'}, 'caiyun': {'use': False, 'color': '#0ff000', 'name': '彩云'},'deepl': {'use': False, 'color': '#0ff000', 'name': 'deepl'}, 'jb7': {'use': False, 'color': '#1839f0', 'name': 'Jbeijing7', 'argsfile': './userconfig/jbj7.json'}, 'kingsoft': {'use': False, 'color': '#1839f0', 'name': '金山快译', 'argsfile': './userconfig/ks.json'}, 'dreye': {'use': False, 'color': '#1839f0', 'name': '快译通', 'argsfile': './userconfig/dreye.json'}, 'sougou2': {'use': False, 'color': '#0ff000', 'name': '搜狗2'}, 'youdao3': {'use': False, 'color': '#0ff000', 'name': '有道3'}, 'youdao4': {'use': False, 'color': '#0ff000', 'name': '有道4'}, 'youdao5': {'use': False, 'color': '#0ff000', 'name': '有道5'},   'tencent': {'use': False, 'color': '#0ff000', 'name': 'TX'},
    # 'ifly': {'use': False, 'color': '#0ff000', 'name': 'ifly'}, 
    'iciba': {'use': False, 'color': '#0ff000', 'name': 'iciba'}, 'baiduapi': {'use': False, 'color': '#0ff000', 'name': '百度api', 'argsfile': './userconfig/baiduapi.json'}, 'tencentapi': {'use': False, 'color': '#0ff000', 'name': '腾讯api', 'argsfile': './userconfig/txapi.json'}, 'byte': {'use': False, 'color': '#0ff000', 'name': 'byte'}, 'qqimt': {'use': False, 'color': '#0ff000', 'name': 'qqimt'}, 'xiaoniu': {'use': False, 'color': '#0ff000', 'name': '小牛api', 'argsfile': './userconfig/xiaoniuapi.json'},
    'huoshan': {'use': False, 'color': '#0ff000', 'name': 'huoshan' },
    'yeekit': {'use': False, 'color': '#0ff000', 'name': 'yeekit' }, 'caiyunapi': {'use': False, 'color': '#0ff000', 'name': '彩云api', 'argsfile': './userconfig/caiyunapi.json'}, 'huoshanapi': {'use': False, 'color': '#0ff000', 'name': '火山api', 'argsfile': './userconfig/huoshanapi.json'},
    'papago': {'use': False, 'color': '#0ff000', 'name': 'papago'},
    'rengong': {'use': False, 'color': '#0ff000', 'name': '人工翻译', 'argsfile': './userconfig/rengong.json'}
    },
     'minifollow': True, 'movefollow': True, 'autostarthook': True, 'translatortimeout': 5, 'minlength': 5, 'maxlength': 150, 'fanjian': 0, 'rotation': 0, 'srclang': 0,
    'transkiroku':False,'transkirokuuse':'baidu',
    'showatcenter':False,
    "mustocr":False,
    "mustocr_interval":5,
    "ocrmininterval":1,
    "selectable":False,
    "autoupdate":False
    
    }

defaultpost = {'_1': {'use': False, 'name': '去除花括号{}'}, '_2': {'use': False, 'name': '去除重复字符(若为1则自动分析去重)', 'args': {'重复次数': 1}}, '_3': {'use': False, 'name': '去除重复行'}, '_4': {
    'use': False, 'name': '过滤HTML标签'}, '_6': {'use': False, 'name': '过滤换行符'},'_9': {'use': False, 'name': '过滤数字和英文字母'}, '_7': {'use': False, 'name': '简单替换内容(若替换为空则直接过滤)', 'args': {'替换内容': {}}},'_8': {'use': False, 'name': '使用正则表达式替换', 'args': {'替换内容': {}}}}

defaulterrorfix = {
    "use": False,
    "dict": {}
}


defaultnoun = {
    "use": False,
    "dict": {}
}
