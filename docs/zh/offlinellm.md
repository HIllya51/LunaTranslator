## 如何使用大模型离线翻译？

### Sakura大模型

> 推荐使用，配置简单，效果好，也可以纯cpu运行轻量模型

部署方法

1. [部署SakuraLLM到Google Colab](/zh/sakurallmcolab.md)


2. 其他部署方法可参考 https://github.com/SakuraLLM/SakuraLLM/wiki

### ChatGPT兼容接口

可以将**Sakura大模型**地址和模型填到这个的参数里面使用（相比起来只是多了些预设prompt等参数，其他无区别）

也可以使用[TGW](https://github.com/oobabooga/text-generation-webui) 、[llama.cpp](https://github.com/ggerganov/llama.cpp) 、[ollama](https://github.com/ollama/ollama)、[one-api](https://github.com/songquanpeng/one-api)之类的工具进行模型的部署，然后将地址和模型填入。

也可以使用Kaggle之类的平台来把模型部署到云端，这时可能会需要用到SECRET_KEY，其他时候可以无视SECRET_KEY参数。

也可以把注册的大模型的api填进来用（但没必要），和注册在线翻译下ChatGPT兼容接口相比，除了不会使用代理外没有其他区别。