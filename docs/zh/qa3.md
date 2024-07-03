## 如何使用离线 chatgpt [^1]

需要在本地或者 ~~ssh 转发端口到本地(能看懂这句话那不需要继续了)~~

仅提供一种解法。别的兼容 gpt api 的都可以。

下载 ollama https://www.ollama.com/

以 llama3 举例。

https://www.ollama.com/library/llama3

下载好模型，后台跑起来后，在

![img](../images/zh/336483101-915f17c5-27a4-465f-9b4e-7a547ba5029f.png)

改成自己在跑的模型，端口改成对应的。就行了。

>PS: 建议使用 https://github.com/SakuraLLM/SakuraLLM/wiki
使用llama.cpp部署，最简单。然后使用sakura大模型的专用接口，里面有一些模型作者写的prompt。

[^1]: [asukaminato0721](https://github.com/HIllya51/LunaTranslator/issues/797)