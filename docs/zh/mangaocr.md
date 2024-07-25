## mangaocr整合包无法启动怎么办？

首次启动start.bat时，会尝试从huggingface上下载模型，但是国内你懂的。

![img](https://image.lunatranslator.xyz/zh/mangaocr/err1.png)

![img](https://image.lunatranslator.xyz/zh/mangaocr/err2.png)

解决方法有两种

1. 魔法上网，可能要开TUN代理

1. 使用vscode，“打开文件夹”打开整合包的文件夹。


![img](https://image.lunatranslator.xyz/zh/mangaocr/fix2.png)

然后使用搜索功能，将“huggingface.co”全部替换成“hf-mirror.com”。由于替换项较多，需要稍微等待一会儿。

![img](https://image.lunatranslator.xyz/zh/mangaocr/fix.png)

然后重新运行start.bat，之后会用国内镜像站下载模型，无须魔法上网。


![img](https://image.lunatranslator.xyz/zh/mangaocr/succ.png)


等待一会儿首次运行的下载模型和每次运行都需要的加载模型。显示“`* Running on http://127.0.0.1:5665`”表示服务已正常启动。