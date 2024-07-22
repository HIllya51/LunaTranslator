## 如何使用大模型离线翻译？

### Sakura大模型

> 这是最推荐使用的，配置最简单，效果最好，也可以纯cpu运行轻量模型

具体部署方法可参考 https://github.com/SakuraLLM/SakuraLLM/wiki

### TGW

可参考 [text-generation-webui](https://github.com/oobabooga/text-generation-webui)进行部署，或使用[懒人包](https://pan.baidu.com/s/1fe7iiHIAtoXW80Twsrv8Nw?pwd=pato)+[非官方教程](https://www.bilibili.com/video/BV1Te411U7me)

!> 看非官方教程弄出了问题别来问我，找发视频的人去。

### ChatGPT兼容接口

可以将**Sakura大模型**和**TGW**的地址和模型填到这个的参数里面使用（相比起来只是多了些预设prompt等参数，其他无区别）

也可以使用[llama.cpp](https://github.com/ggerganov/llama.cpp) 、[ollama](https://github.com/ollama/ollama)、[one-api](https://github.com/songquanpeng/one-api)之类的工具进行模型的部署，然后将地址和模型填入。

也可以使用Kaggle之类的平台来把模型部署到云端，这时可能会需要用到SECRET_KEY，其他时候可以无视SECRET_KEY参数。

也可以把注册的大模型的api填进来用（但没必要），和注册在线翻译下ChatGPT兼容接口相比，除了不会使用代理外没有其他区别。