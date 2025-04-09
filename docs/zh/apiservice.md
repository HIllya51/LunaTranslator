# 网络服务

## Web页面

1. #### /page/mainui

    与主窗口显示的文本内容同步

1. #### /page/transhist

    与历史文本显示的文本内容同步

1. #### /page/dictionary

    查询单词页面。在/page/mainui中进行点击单词查词时会唤出该页面。

1. #### /

    整合上述三个页面的一个页面。在该窗口中的/page/mainui子区域中进行点击单词查词时，不会打开新的查词窗口，而是会在当前窗口的/page/dictionary子区域中进行查词

1. #### /page/translate

    翻译界面

1. #### /page/ocr

    OCR界面

## API服务

### HTTP服务

1. #### /api/translate
    
    必须指定查询参数`text`

    如果指定参数`id`（翻译器的ID），则会使用该翻译器进行翻译，否则会返回最快的翻译接口

    返回`application/json`，包含翻译器ID`id`、名称`name`和翻译结果`result`

1. #### /api/dictionary

    必须指定查询参数`word`

    如果指定参数`id`（词典的ID），则会返回该词典的查询结果的`application/json`对象，包含词典ID`id`、词典名称`name`和HTML内容`result`。如果查询失败则会返回一个空的对象。

    否则会查询所有词典，返回`event/text-stream`，每个event为一个JSON对象，包含词典ID`id`、词典名称`name`和HTML内容`result`

1. #### /api/mecab
    
    必须指定查询参数`text`

    返回Mecab对`text`的解析结果

1. #### /api/tts
    
    必须指定查询参数`text`

    返回音频二进制

1. #### /api/ocr
    
    使用POST方法，发送json请求，包含`image`字段，内容为base64编码的图像。

1. #### /api/list/dictionary

    列出当前可用的辞书

1. #### /api/list/translator

    列出当前可用的翻译器


### WebSocket服务

1.  #### /api/ws/text/origin

    会持续输出所有提取到的原文文本

1.  #### /api/ws/text/trans

    会持续输出所有翻译结果
