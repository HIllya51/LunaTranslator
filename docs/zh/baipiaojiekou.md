## 可白嫖的大模型API

### **deepinfra**

**API接口地址** `https://api.deepinfra.com/v1/openai/chat/completions` 

**API Key** **必须把API Key设为空，否则会报错**

**model** 可以在 [https://deepinfra.com/chat](https://deepinfra.com/chat) 查看当前可用的模型。截止到撰写文档时，可以免费使用的模型是：`meta-llama/Meta-Llama-3.1-405B-Instruct` `meta-llama/Meta-Llama-3.1-70B-Instruct` `meta-llama/Meta-Llama-3.1-8B-Instruct` `mistralai/Mixtral-8x22B-Instruct-v0.1` `mistralai/Mixtral-8x7B-Instruct-v0.1` `microsoft/WizardLM-2-8x22B` `microsoft/WizardLM-2-7B` `Qwen/Qwen2.5-72B-Instruct` `Qwen/Qwen2-72B-Instruct` `Qwen/Qwen2-7B-Instruct` `microsoft/Phi-3-medium-4k-instruct` `google/gemma-2-27b-it` `openbmb/MiniCPM-Llama3-V-2_5` `mistralai/Mistral-7B-Instruct-v0.3` `lizpreciatior/lzlv_70b_fp16_hf` `openchat/openchat_3.5` `openchat/openchat-3.6-8b` `Phind/Phind-CodeLlama-34B-v2` `Gryphe/MythoMax-L2-13b` `cognitivecomputations/dolphin-2.9.1-llama-3-70b`

### **cerebras**


**API接口地址** `https://api.cerebras.ai/v1/chat/completions` 

**model** 支持`llama3.1-8b` `llama3.1-70b`

**API Key** 在 [https://inference.cerebras.ai](https://inference.cerebras.ai/) 选择模型随意发送消息后进行抓包，查看当前 `标头` -> `请求标头` -> `Authorization` 的值，其为 `Bearer demo-xxxxhahaha` ，其中 `demo-xxxxhahaha` 即为API Key

![img](https://image.lunatranslator.org/zh/damoxing/cerebras.png) 
