# 网络服务

## Web页面

1. #### /page/mainui

    与主窗口显示的文本内容同步

1. #### /page/transhist

    与历史文本显示的文本内容同步

1. #### /page/searchword

    查询单词页面。在/page/mainui中进行点击单词查词时会唤出该页面。

1. #### /

    整合上述三个页面的一个页面。在该窗口中的/page/mainui子区域中进行点击单词查词时，不会打开新的查词窗口，而是会在当前窗口的/page/searchword子区域中进行查词

## API服务

### HTTP服务

1. #### /api/searchword

    需要查询参数`word`

    返回`event/text-stream`，每个event为一个JSON对象，包含词典名称`name`和HTML内容`result`

### WebSocket服务

1.  #### /api/ws/text/origin

    会持续输出所有提取到的原文文本

1.  #### /api/ws/text/trans

    会持续输出所有翻译结果
