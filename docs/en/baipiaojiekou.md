## Freely Available Large Model APIs

### **DeepInfra**

**API Endpoint** `https://api.deepinfra.com/v1/openai/chat/completions`

**API Key** **The API Key must be set to empty, otherwise it will result in an error.**

**Model** You can view the currently available models at [https://deepinfra.com/chat](https://deepinfra.com/chat). As of the time of writing this document, the freely available models are: `meta-llama/Meta-Llama-3.1-405B-Instruct` `meta-llama/Meta-Llama-3.1-70B-Instruct` `meta-llama/Meta-Llama-3.1-8B-Instruct` `mistralai/Mixtral-8x22B-Instruct-v0.1` `mistralai/Mixtral-8x7B-Instruct-v0.1` `microsoft/WizardLM-2-8x22B` `microsoft/WizardLM-2-7B` `Qwen/Qwen2.5-72B-Instruct` `Qwen/Qwen2-72B-Instruct` `Qwen/Qwen2-7B-Instruct` `microsoft/Phi-3-medium-4k-instruct` `google/gemma-2-27b-it` `openbmb/MiniCPM-Llama3-V-2_5` `mistralai/Mistral-7B-Instruct-v0.3` `lizpreciatior/lzlv_70b_fp16_hf` `openchat/openchat_3.5` `openchat/openchat-3.6-8b` `Phind/Phind-CodeLlama-34B-v2` `Gryphe/MythoMax-L2-13b` `cognitivecomputations/dolphin-2.9.1-llama-3-70b`

### **Cerebras**

**API Endpoint** `https://api.cerebras.ai/v1/chat/completions`

**Model** Supports `llama3.1-8b` `llama3.1-70b`

**API Key** After selecting a model and sending a message on [https://inference.cerebras.ai](https://inference.cerebras.ai/), you can intercept the request and check the current `Headers` -> `Request Headers` -> `Authorization` value, which is `Bearer demo-xxxxhahaha`, where `demo-xxxxhahaha` is the API Key.

![Cerebras API Key](https://image.lunatranslator.org/zh/damoxing/cerebras.png)