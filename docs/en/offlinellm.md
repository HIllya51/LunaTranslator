## How to Use Large Model Offline Translation?

### Sakura Large Model

> Recommended for use, simple configuration, good results, and can also run lightweight models purely on CPU.

Deployment Methods

1. [Deploy SakuraLLM to an Online GPU Platform](/zh/sakurallmcolab.md)

2. Other deployment methods can be referred to at https://github.com/SakuraLLM/SakuraLLM/wiki

### ChatGPT Compatible Interface

You can fill in the **Sakura Large Model** address and model into the parameters of this interface (compared to this, it only adds some preset prompts and other parameters, with no other differences).

You can also use tools like [TGW](https://github.com/oobabooga/text-generation-webui), [llama.cpp](https://github.com/ggerganov/llama.cpp), [ollama](https://github.com/ollama/ollama), [one-api](https://github.com/songquanpeng/one-api) to deploy models, and then fill in the address and model.

You can also use platforms like Kaggle to deploy models to the cloud, in which case you may need to use SECRET_KEY; otherwise, you can ignore the SECRET_KEY parameter.

You can also fill in the API of the registered large model (but it's unnecessary), and compared to the ChatGPT compatible interface under registered online translation, the only difference is that it does not use a proxy.