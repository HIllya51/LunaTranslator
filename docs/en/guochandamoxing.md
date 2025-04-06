# Large Model Online Translation

::: details Using Multiple Large Model Interfaces Simultaneously?
If you only have multiple different keys and want to poll them, simply separate them with `|`.

However, sometimes you may want to use multiple different API interface addresses, prompts, models, or parameters simultaneously to compare translation results. Here's how:

1. Click the "+" button at the bottom right.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
2. A window will pop up. Select the general large model interface and give it a name. This will duplicate the current settings and API of the general large model interface.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
3. Activate the duplicated interface and configure it separately. The duplicated interface can run alongside the original one, allowing you to use multiple different settings simultaneously.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: info
Most **API interface addresses** can be selected from the dropdown list, but some may be missing. For other interfaces not listed, please refer to their documentation to fill in the details.
:::

::: tip
**Model** can be selected from the dropdown list, and some interfaces can dynamically fetch the model list based on the **API interface address** and **API Key**. After filling in these two fields, click the refresh button next to **model** to get the available model list.

If the platform does not support fetching models via an API and the default list does not include the model you need, please refer to the official documentation of the interface to manually fill in the model.
:::

### Foreign Large Model Interfaces

::: tabs

== OpenAI

**API Interface Address** `https://api.openai.com/v1`

**API Key** https://platform.openai.com/api-keys

**Model** https://platform.openai.com/docs/models

== Gemini

**API Interface Address** `https://generativelanguage.googleapis.com`

**API Key** https://aistudio.google.com/app/apikey

**Model** https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models

== Claude

**API Interface Address** `https://api.anthropic.com/v1/messages`

**API Key** https://console.anthropic.com/

**Model** https://docs.anthropic.com/en/docs/about-claude/models

== Cohere

**API Interface Address** `https://api.cohere.ai/compatibility/v1`

**API Key** https://dashboard.cohere.com/api-keys

**Model** https://docs.cohere.com/docs/models

== x.ai

**API Interface Address** `https://api.x.ai/`

**API Key** https://console.x.ai/

== Groq

**API Interface Address** `https://api.groq.com/openai/v1/chat/completions`

**API Key** https://console.groq.com/keys

**Model** https://console.groq.com/docs/models Fill in the `Model ID`

== OpenRouter

**API Interface Address** `https://openrouter.ai/api/v1/chat/completions`

**API Key** https://openrouter.ai/settings/keys

**Model** https://openrouter.ai/docs/models

== Mistral AI

**API Interface Address** `https://api.mistral.ai/v1/chat/completions`

**API Key** https://console.mistral.ai/api-keys/

**Model** https://docs.mistral.ai/getting-started/models/

== Azure

**API Interface Address** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

Replace `{endpoint}` and `{deployName}` with your endpoint and deployName.

== Deepinfra

**API Interface Address** `https://api.deepinfra.com/v1/openai/chat/completions`

**API Key** https://deepinfra.com/dash/api_keys

== Cerebras

**API Interface Address** `https://api.cerebras.ai/v1/chat/completions`

**Model** Supports `llama3.1-8b`, `llama3.1-70b`, `llama-3.3-70b`

**API Key** Go to [https://inference.cerebras.ai](https://inference.cerebras.ai/), select a model, send a message, and then capture the request. Check the `Headers` -> `Request Headers` -> `Authorization` value, which will be `Bearer demo-xxxxhahaha`. The `demo-xxxxhahaha` part is the API Key.

![img](https://image.lunatranslator.org/zh/damoxing/cerebras.png)

:::

### Domestic Large Model Interfaces

::: tabs

== DeepSeek

**API Interface Address** `https://api.deepseek.com`

**API Key** https://platform.deepseek.com/api_keys

**Model** https://platform.deepseek.com/api-docs/zh-cn/pricing

== Alibaba Cloud Bailian Large Model

**API Interface Address** `https://dashscope.aliyuncs.com/compatible-mode/v1`

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**Model** https://help.aliyun.com/zh/model-studio/getting-started/models

== ByteDance Doubao Large Model

**API Interface Address** `https://ark.cn-beijing.volces.com/api/v3`

**API Key** [Create API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) to obtain.

**Model** After [creating an inference endpoint](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10), fill in the **endpoint** instead of the **model**.

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

== Moonshot AI

**API Interface Address** `https://api.moonshot.cn`

**API Key** https://platform.moonshot.cn/console/api-keys

**Model** https://platform.moonshot.cn/docs/intro

== Zhipu AI

**API Interface Address** `https://open.bigmodel.cn/api/paas/v4/chat/completions`

**API Key** https://bigmodel.cn/usercenter/apikeys

**Model** https://bigmodel.cn/dev/howuse/model

== Lingyi Wanwu

**API Interface Address** `https://api.lingyiwanwu.com`

**API Key** https://platform.lingyiwanwu.com/apikeys

**Model** https://platform.lingyiwanwu.com/docs/api-reference#list-models

== SiliconFlow

**API Interface Address** `https://api.siliconflow.cn`

**API Key** https://cloud-hk.siliconflow.cn/account/ak

**Model** https://docs.siliconflow.cn/docs/model-names

== iFlytek Spark Large Model

**API Interface Address** `https://spark-api-open.xf-yun.com/v1`

**API Key** Refer to the [official documentation](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E) to obtain the **APIKey** and **APISecret**, then fill in the format `APIKey:APISecret`.

**Model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== Tencent Hunyuan Large Model

**API Interface Address** `https://api.hunyuan.cloud.tencent.com/v1`

**API Key** Refer to the [official documentation](https://cloud.tencent.com/document/product/1729/111008)

**Model** https://cloud.tencent.com/document/product/1729/97731

== Baidu Qianfan Large Model

**API Interface Address** `https://qianfan.baidubce.com/v2`

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**Model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key** should be generated using Baidu Intelligent Cloud IAM's Access Key and Secret Key to create the BearerToken for the interface, or directly fill in the format `Access Key`:`Secret Key` in the **API Key** field. Note that this is not the API Key and Secret Key for the old v1 version of Qianfan ModelBuilder; they are not interchangeable.

== MiniMax

**API Interface Address** `https://api.minimax.chat/v1`

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

**Model** https://platform.minimaxi.com/document/Models?key=66701cb01d57f38758d581a4

:::