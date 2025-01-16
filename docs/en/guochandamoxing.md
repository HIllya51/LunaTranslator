# Large Model API for Translation

::: details How to use multiple ChatGPT-compatible interfaces (or dedicated interfaces) simultaneously?
If you simply have multiple different keys and want to poll them, just separate them with a `|`.

However, sometimes you want to use multiple different API addresses/prompts/models/parameters at the same time to compare translation effects. The method is:

Click the "+" button at the bottom right
![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
A window will pop up, select ChatGPT-compatible interface (or dedicated interface), and give it a name. This will copy the current ChatGPT-compatible interface (or dedicated interface) settings and API.
![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
Activate the copied interface and you can make individual settings. The copied interface can run with the original interface, allowing you to use multiple different settings.
![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: tip
**model** can be selected from a dropdown list, and some interfaces can dynamically fetch the model list based on the **API Interface Address** and **API Key**. After filling in these two fields, click the refresh button next to **model** to obtain the available model list. 

If the platform does not support the model retrieval interface and the default list does not include the required model, please refer to the official API documentation to manually enter the model.

:::

## ChatGPT-Compatible Interfaces


::: info
Most large model platforms use ChatGPT-compatible interfaces.

Since there are so many platforms, it's impossible to list them all. For other interfaces not listed, please refer to their documentation to fill in the corresponding parameters.
:::

#### Foreign Large Model Interfaces

::: tabs

== OpenAI

**API Interface Address** `https://api.openai.com/v1` 

**API Key** https://platform.openai.com/api-keys

**model** https://platform.openai.com/docs/models

== x.ai

**API Interface Address** `https://api.x.ai/`

**API Key** https://console.x.ai/

== groq

**API Interface Address** `https://api.groq.com/openai/v1/chat/completions` 

**API Key** https://console.groq.com/keys 

**model** https://console.groq.com/docs/models  Fill in `Model ID`

== OpenRouter

**API Interface Address** `https://openrouter.ai/api/v1/chat/completions` 

**API Key** https://openrouter.ai/settings/keys 

**model** https://openrouter.ai/docs/models 

== Mistral AI

**API Interface Address** `https://api.mistral.ai/v1/chat/completions` 

**API Key** https://console.mistral.ai/api-keys/ 

**model** https://docs.mistral.ai/getting-started/models/ 

== Azure

**API Endpoint URL** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

Replace `{endpoint}` and `{deployName}` with your endpoint and deployName.

== DeepInfra

**API Endpoint** `https://api.deepinfra.com/v1/openai/chat/completions`

**API Key** https://deepinfra.com/dash/api_keys

== Cerebras

**API Endpoint** `https://api.cerebras.ai/v1/chat/completions`

**Model** Supports `llama3.1-8b` `llama3.1-70b` `llama-3.3-70b`

**API Key** After selecting a model and sending a message on [https://inference.cerebras.ai](https://inference.cerebras.ai/), you can intercept the request and check the current `Headers` -> `Request Headers` -> `Authorization` value, which is `Bearer demo-xxxxhahaha`, where `demo-xxxxhahaha` is the API Key.

![Cerebras API Key](https://image.lunatranslator.org/zh/damoxing/cerebras.png)

:::

#### Domestic Large Model Interfaces

::: tabs

== DeepSeek

**API Interface Address** `https://api.deepseek.com` 

**API Key** https://platform.deepseek.com/api_keys 

**model** https://platform.deepseek.com/api-docs/zh-cn/pricing 

== Alibaba Cloud Bailian Large Model

**API Interface Address** `https://dashscope.aliyuncs.com/compatible-mode/v1` 

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key 

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== ByteDance DouBao Large Model

**API Interface Address** `https://ark.cn-beijing.volces.com/api/v3` 

**API Key** [Create API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) to obtain 

**model** [Create Inference Access Point](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10), fill in **Access Point** instead of **Model** 

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png) 

== Moonshot AI

**API Interface Address** `https://api.moonshot.cn` 

**API Key** https://platform.moonshot.cn/console/api-keys 

**model** https://platform.moonshot.cn/docs/intro 

== Zhipu AI

**API Interface Address** `https://open.bigmodel.cn/api/paas/v4/chat/completions` 

**API Key** https://bigmodel.cn/usercenter/apikeys 

**model** https://bigmodel.cn/dev/howuse/model 

== Lingyiwanwu

**API Interface Address** `https://api.lingyiwanwu.com` 

**API Key** https://platform.lingyiwanwu.com/apikeys 

**model** https://platform.lingyiwanwu.com/docs/api-reference#list-models 

== SiliconFlow

**API Interface Address** `https://api.siliconflow.cn` 

**API Key** https://cloud-hk.siliconflow.cn/account/ak 

**model** https://docs.siliconflow.cn/docs/model-names 

== iFlytek Spark Large Model

**API Interface Address** `https://spark-api-open.xf-yun.com/v1` 

**API Key** Refer to the [official documentation](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B7%E6%B1%82%E6%B1%82%E8%AF%B7%E6%B1%82%E6%B1%82%E8%AF%B7%E6%B1%82) to obtain **APIKey** and **APISecret**, fill in according to the format of **APIKey:APISecret** 

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0 

== Tencent Hunyuan Large Model

**API Interface Address** `https://api.hunyuan.cloud.tencent.com/v1`

**API Key** Refer to the [official documentation](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

== Baidu Qianfan Large Model

**API Interface Address** `https://qianfan.baidubce.com/v2`

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>For the **API Key**, please use the Access Key and Secret Key from Baidu AI Cloud IAM to generate a Bearer Token, which should then be entered as the **API Key**, or directly enter both in the format `{Access Key}:{Secret Key}` in the **API Key** field. Note that this is different from the API Key and Secret Key for the old v1 version of Qianfan ModelBuilder; they are not interchangeable.

:::

## Dedicated Interfaces for Specific Platforms

::: info
Some large model platforms are not fully compatible with the ChatGPT interface, please fill in the parameters to use in the dedicated interface.
:::

::: tabs

== gemini

<a id="gemini"></a>

**API Interface Address** `https://generativelanguage.googleapis.com`

**API Key** https://aistudio.google.com/app/apikey 

**model** https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models 

== claude

**API Interface Address** `https://api.anthropic.com` 

**API Key** https://console.anthropic.com/ 

**model**  https://docs.anthropic.com/en/docs/about-claude/models 

== cohere

**API Key** https://dashboard.cohere.com/api-keys 

**model** https://docs.cohere.com/docs/models 

:::