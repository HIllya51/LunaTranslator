## 如何使用大模型离线翻译？

### Sakura大模型

> 这是最推荐使用的，配置最简单，效果最好，也可以纯cpu运行轻量模型

具体部署方法可参考 https://github.com/SakuraLLM/SakuraLLM/wiki

### TGW

可参考 [text-generation-webui](https://github.com/oobabooga/text-generation-webui)进行部署，或使用[懒人包](https://pan.baidu.com/s/1fe7iiHIAtoXW80Twsrv8Nw?pwd=pato)+[非官方教程](https://www.bilibili.com/video/BV1Te411U7me)

!> 看非官方教程弄出了问题别来问我，找发视频的人去。

### ChatGPT兼容接口

其实**Sakura大模型**和**TGW**的接口基本和**ChatGPT兼容接口**一样，只不过多了一点预设的prompt和参数而已。可以把sakura和TGW的地址和模型填到这个的参数里面使用。

也可以使用**oneapi**、**ollama**之类的工具进行模型的部署，然后将地址和模型填入。

也可以使用Kaggle之类的平台来把模型部署到云端，这时可能会需要用到SECRET_KEY，其他时候可以无视SECRET_KEY参数。
