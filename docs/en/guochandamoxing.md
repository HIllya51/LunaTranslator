## How to Use Large Model API for Translation

<details>
  <summary>How to use multiple ChatGPT-compatible interfaces (or dedicated interfaces) simultaneously?</summary>
  If you simply have multiple different keys and want to poll them, just separate them with a `|`.<br>
  However, sometimes you want to use multiple different API addresses/prompts/models/parameters at the same time to compare translation effects. The method is:<br>
  Click the "+" button at the bottom right
  <img src="https://image.lunatranslator.org/zh/damoxing/extraapi1.png"> 
  A window will pop up, select ChatGPT-compatible interface (or dedicated interface), and give it a name. This will copy the current ChatGPT-compatible interface (or dedicated interface) settings and API.
  <img src="https://image.lunatranslator.org/zh/damoxing/extraapi2.png"> 
  Activate the copied interface and you can make individual settings. The copied interface can run with the original interface, allowing you to use multiple different settings.
  <img src="https://image.lunatranslator.org/zh/damoxing/extraapi3.png"> 
</details>

>**model** can be selected from the drop-down list, and if it's not in the list, you can manually enter/modify it according to the official documentation of the interface.<br>
>Some interfaces can dynamically obtain the model list based on **API Interface Address** and **API Key**. After filling in these two items, click the refresh button next to **model** to get the list of available models.

### ChatGPT-Compatible Interfaces

>Most large model platforms use ChatGPT-compatible interfaces.<br>Since there are so many platforms, it's impossible to list them all. For other interfaces not listed, please refer to their documentation to fill in the corresponding parameters.

#### Foreign Large Model Interfaces

<!-- tabs:start -->

### **OpenAI**

**API Interface Address** `https://api.openai.com/v1` 

**API Key** https://platform.openai.com/api-keys

**model** https://platform.openai.com/docs/models

### **groq**

**API Interface Address** `https://api.groq.com/openai/v1/chat/completions` 

**API Key** https://console.groq.com/keys 

**model** https://console.groq.com/docs/models  Fill in `Model ID`

### **OpenRouter**

**API Interface Address** `https://openrouter.ai/api/v1/chat/completions` 

**API Key** https://openrouter.ai/settings/keys 

**model** https://openrouter.ai/docs/models 

### **Mistral AI**

**API Interface Address** `https://api.mistral.ai/v1/chat/completions` 

**API Key** https://console.mistral.ai/api-keys/ 

**model** https://docs.mistral.ai/getting-started/models/ 

### **Azure**

**API Endpoint URL** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

Replace `{endpoint}` and `{deployName}` with your endpoint and deployName.

### **DeepInfra**

**API Endpoint** `https://api.deepinfra.com/v1/openai/chat/completions`

**API Key** **The API Key must be set to empty, otherwise it will result in an error.**

**Model** You can view the currently available models at [https://deepinfra.com/chat](https://deepinfra.com/chat). As of the time of writing this document, the freely available models are: `meta-llama/Meta-Llama-3.1-405B-Instruct` `meta-llama/Meta-Llama-3.1-70B-Instruct` `meta-llama/Meta-Llama-3.1-8B-Instruct` `mistralai/Mixtral-8x22B-Instruct-v0.1` `mistralai/Mixtral-8x7B-Instruct-v0.1` `microsoft/WizardLM-2-8x22B` `microsoft/WizardLM-2-7B` `Qwen/Qwen2.5-72B-Instruct` `Qwen/Qwen2-72B-Instruct` `Qwen/Qwen2-7B-Instruct` `microsoft/Phi-3-medium-4k-instruct` `google/gemma-2-27b-it` `openbmb/MiniCPM-Llama3-V-2_5` `mistralai/Mistral-7B-Instruct-v0.3` `lizpreciatior/lzlv_70b_fp16_hf` `openchat/openchat_3.5` `openchat/openchat-3.6-8b` `Phind/Phind-CodeLlama-34B-v2` `Gryphe/MythoMax-L2-13b` `cognitivecomputations/dolphin-2.9.1-llama-3-70b`

### **Cerebras**

**API Endpoint** `https://api.cerebras.ai/v1/chat/completions`

**Model** Supports `llama3.1-8b` `llama3.1-70b`

**API Key** After selecting a model and sending a message on [https://inference.cerebras.ai](https://inference.cerebras.ai/), you can intercept the request and check the current `Headers` -> `Request Headers` -> `Authorization` value, which is `Bearer demo-xxxxhahaha`, where `demo-xxxxhahaha` is the API Key.

![Cerebras API Key](https://image.lunatranslator.org/zh/damoxing/cerebras.png)

<!-- tabs:end -->

#### Domestic Large Model Interfaces

<!-- tabs:start -->

### **DeepSeek**

**API Interface Address** `https://api.deepseek.com` 

**API Key** https://platform.deepseek.com/api_keys 

**model** https://platform.deepseek.com/api-docs/zh-cn/pricing 

### **Alibaba Cloud Bailian Large Model**

**API Interface Address** `https://dashscope.aliyuncs.com/compatible-mode/v1` 

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key 

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

### **ByteDance DouBao Large Model**

**API Interface Address** `https://ark.cn-beijing.volces.com/api/v3` 

**API Key** [Create API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) to obtain 

**model** [Create Inference Access Point](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10), fill in **Access Point** instead of **Model** 

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png) 

### **Moonshot AI**

**API Interface Address** `https://api.moonshot.cn` 

**API Key** https://platform.moonshot.cn/console/api-keys 

**model** https://platform.moonshot.cn/docs/intro 

### **Zhipu AI**

**API Interface Address** `https://open.bigmodel.cn/api/paas/v4/chat/completions` 

**API Key** https://bigmodel.cn/usercenter/apikeys 

**model** https://bigmodel.cn/dev/howuse/model 

### **Lingyiwanwu**

**API Interface Address** `https://api.lingyiwanwu.com` 

**API Key** https://platform.lingyiwanwu.com/apikeys 

**model** https://platform.lingyiwanwu.com/docs/api-reference#list-models 

### **SiliconFlow**

**API Interface Address** `https://api.siliconflow.cn` 

**API Key** https://cloud-hk.siliconflow.cn/account/ak 

**model** https://docs.siliconflow.cn/docs/model-names 

### **iFlytek Spark Large Model**

**API Interface Address** `https://spark-api-open.xf-yun.com/v1` 

**API Key** Refer to the [official documentation](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B7%E6%B1%82%E6%B1%82%E8%AF%B7%E6%B1%82%E6%B1%82%E8%AF%B7%E6%B1%82) to obtain **APIKey** and **APISecret**, fill in according to the format of **APIKey:APISecret** 

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0 

<!-- tabs:end -->

### Dedicated Interfaces for Specific Platforms

>Some large model platforms are not fully compatible with the ChatGPT interface, please fill in the parameters to use in the dedicated interface.

#### Foreign Large Model Interfaces

<!-- tabs:start -->

### **gemini**

<a id="gemini"></a>

**model** https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models 

**API Key** https://aistudio.google.com/app/apikey 

### **claude**

**BASE_URL** `https://api.anthropic.com` 

**API_KEY** https://console.anthropic.com/ 

**model**  https://docs.anthropic.com/en/docs/about-claude/models 

### **cohere**

**API Key** https://dashboard.cohere.com/api-keys 

**model** https://docs.cohere.com/docs/models 

<!-- tabs:end -->

#### Domestic Large Model Interfaces

<!-- tabs:start -->

### **Tencent Hunyuan Large Model**

**SecretId** & **SecretKey** https://console.cloud.tencent.com/cam/capi 

**model** https://cloud.tencent.com/document/product/1729/97731 

### **Baidu Qianfan Large Model**

!> This model seems to only support Chinese-English translation and does not support Japanese.

**model** Should fill in the tail of the **Request Address** in the Baidu interface documentation, for example:

![img](https://image.lunatranslator.org/zh/damoxing/qianfan1.png) 

![img](https://image.lunatranslator.org/zh/damoxing/qianfan2.png) 

<!-- tabs:end -->