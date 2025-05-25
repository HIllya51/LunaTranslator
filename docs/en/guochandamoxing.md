# Large Model Translation Interface

## Large Model Online Translation

::: details Using Multiple Large Model Interfaces Simultaneously?
If you only have multiple different keys and want to poll them, simply separate them with `|`.

However, sometimes you may want to use multiple different API interface addresses, prompts, models, or parameters simultaneously to compare translation results. Here's how:

1. Click the "+" button above.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
1. A window will pop up. Select the general large model interface and give it a name. This will duplicate the current settings and API of the general large model interface.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
1. Activate the duplicated interface and configure it separately. The duplicated interface can run alongside the original one, allowing you to use multiple different settings simultaneously.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: info
Most **API interface addresses** can be selected from the dropdown list, but some may be missing. For other interfaces not listed, please refer to their documentation to fill in the details.
:::

::: tip
**model** can be selected from the dropdown list, and some interfaces can dynamically fetch the model list based on the **API interface address** and **API Key**. After filling in these two fields, click the refresh button next to **model** to get the available model list.

If the platform does not support fetching models via an API and the default list does not include the model you need, please refer to the official documentation of the interface to manually fill in the model.
:::

### Foreign Large Model Interfaces

::: tabs

== OpenAI

**API Key** https://platform.openai.com/api-keys

== Gemini

**API Key** https://aistudio.google.com/app/apikey

== Claude

**API Key** https://console.anthropic.com/

**model** https://docs.anthropic.com/en/docs/about-claude/models

== Cohere

**API Key** https://dashboard.cohere.com/api-keys

== x.ai

**API Key** https://console.x.ai/

== Groq

**API Key** https://console.groq.com/keys

== OpenRouter

**API Key** https://openrouter.ai/settings/keys

== Mistral AI

**API Key** https://console.mistral.ai/api-keys/

== Azure

**API Interface Address** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

Replace `{endpoint}` and `{deployName}` with your endpoint and deployName.

== Deepinfra

**API Key** https://deepinfra.com/dash/api_keys

== Cerebras

**API Key** https://cloud.cerebras.ai/  ->  API Keys

== Chutes

**API Key** https://chutes.ai/app/api

:::

### Domestic Large Model Interfaces

::: tabs

== DeepSeek

**API Key** https://platform.deepseek.com/api_keys

== Alibaba Cloud Bailian Large Model

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

== ByteDance Volcano Engine

**API Key** [Create API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) to obtain.

**model** After [creating an inference endpoint](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10), fill in the **endpoint** instead of the **model**.

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

== Moonshot AI

**API Key** https://platform.moonshot.cn/console/api-keys

== Zhipu AI

**API Key** https://bigmodel.cn/usercenter/apikeys

== Lingyi Wanwu

**API Key** https://platform.lingyiwanwu.com/apikeys

== SiliconFlow

**API Key** https://cloud-hk.siliconflow.cn/account/ak

== iFlytek Spark Large Model

**API Key** Refer to the [official documentation](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E) to obtain the **APIKey** and **APISecret**, then fill in the format `APIKey:APISecret`.

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== Tencent Hunyuan Large Model

**API Key** Refer to the [official documentation](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

== Baidu Qianfan Large Model

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key** should be generated using Baidu Intelligent Cloud IAM's Access Key and Secret Key to create the BearerToken for the interface, or directly fill in the format `Access Key`:`Secret Key` in the **API Key** field. Note that this is not the API Key and Secret Key for the old v1 version of Qianfan ModelBuilder; they are not interchangeable.

== MiniMax

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

:::

## Large Model Offline Translation

### General Large Model Interface


You can also use tools like [llama.cpp](https://github.com/ggerganov/llama.cpp), [ollama](https://github.com/ollama/ollama), [one-api](https://github.com/songquanpeng/one-api) to deploy models, and then fill in the address and model.

You can also use platforms like Kaggle to deploy models to the cloud, in which case you may need to use SECRET_KEY; otherwise, you can ignore the SECRET_KEY parameter.