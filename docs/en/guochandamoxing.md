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
**model** can be selected from the dropdown list, and some interfaces can dynamically fetch the model list based on the **API interface address** and **API Key**. After filling in these two fields, click the refresh button next to **model** to get the available model list.

If the platform does not support fetching models via an API and the default list does not include the model you need, please refer to the official documentation of the interface to manually fill in the model.
:::

### Foreign Large Model Interfaces

::: tabs

== OpenAI

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.openai.com/v1`</del>

**API Key** https://platform.openai.com/api-keys

**model** Selectable from the drop-down list in the software [~~https://platform.openai.com/docs/models~~](https://platform.openai.com/docs/models)

== Gemini

**API Interface Address** Selectable from the drop-down list in the software <del>`https://generativelanguage.googleapis.com`</del>

**API Key** https://aistudio.google.com/app/apikey

**model** Selectable from the drop-down list in the software [~~https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models~~](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

== Claude

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.anthropic.com/v1/messages`</del>

**API Key** https://console.anthropic.com/

**model** https://docs.anthropic.com/en/docs/about-claude/models

== Cohere

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.cohere.ai/compatibility/v1`</del>

**API Key** https://dashboard.cohere.com/api-keys

**model** Selectable from the drop-down list in the software [~~https://docs.cohere.com/docs/models~~](https://docs.cohere.com/docs/models)

== x.ai

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.x.ai/`</del>

**API Key** https://console.x.ai/

**model** Selectable from the drop-down list in the software

== Groq

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.groq.com/openai/v1/chat/completions`</del>

**API Key** https://console.groq.com/keys

**model** Selectable from the drop-down list in the software [~~https://console.groq.com/docs/models~~](https://console.groq.com/docs/models)

== OpenRouter

**API Interface Address** Selectable from the drop-down list in the software <del>`https://openrouter.ai/api/v1/chat/completions`</del>

**API Key** https://openrouter.ai/settings/keys

**model** Selectable from the drop-down list in the software [~~https://openrouter.ai/docs/models~~](https://openrouter.ai/docs/models)

== Mistral AI

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.mistral.ai/v1/chat/completions`</del>

**API Key** https://console.mistral.ai/api-keys/

**model** Selectable from the drop-down list in the software [~~https://docs.mistral.ai/getting-started/models/~~](https://docs.mistral.ai/getting-started/models/)

== Azure

**API Interface Address** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

Replace `{endpoint}` and `{deployName}` with your endpoint and deployName.

== Deepinfra

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.deepinfra.com/v1/openai/chat/completions`</del>

**API Key** https://deepinfra.com/dash/api_keys

**model** Selectable from the drop-down list in the software

== Cerebras

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.cerebras.ai/v1/chat/completions`</del>

**API Key** https://cloud.cerebras.ai/  ->  API Keys

**model** Selectable from the drop-down list in the software

:::

### Domestic Large Model Interfaces

::: tabs

== DeepSeek

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.deepseek.com`</del>

**API Key** https://platform.deepseek.com/api_keys

**model** Selectable from the drop-down list in the software [~~https://api-docs.deepseek.com/zh-cn/quick_start/pricing~~](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)

== Alibaba Cloud Bailian Large Model

**API Interface Address** Selectable from the drop-down list in the software <del>`https://dashscope.aliyuncs.com/compatible-mode/v1`</del>

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== ByteDance Doubao Large Model

**API Interface Address** Selectable from the drop-down list in the software <del>`https://ark.cn-beijing.volces.com/api/v3`</del>

**API Key** [Create API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) to obtain.

**model** After [creating an inference endpoint](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10), fill in the **endpoint** instead of the **model**.

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

== Moonshot AI

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.moonshot.cn`</del>

**API Key** https://platform.moonshot.cn/console/api-keys

**model** Selectable from the drop-down list in the software [~~https://platform.moonshot.cn/docs/intro~~](https://platform.moonshot.cn/docs/intro)

== Zhipu AI

**API Interface Address** Selectable from the drop-down list in the software <del>`https://open.bigmodel.cn/api/paas/v4/chat/completions`</del>

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

== Lingyi Wanwu

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.lingyiwanwu.com`</del>

**API Key** https://platform.lingyiwanwu.com/apikeys

**model** Selectable from the drop-down list in the software [~~https://platform.lingyiwanwu.com/docs/api-reference#list-models~~](https://platform.lingyiwanwu.com/docs/api-reference#list-models)

== SiliconFlow

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.siliconflow.cn`</del>

**API Key** https://cloud-hk.siliconflow.cn/account/ak

**model** Selectable from the drop-down list in the software [~~https://docs.siliconflow.cn/docs/model-names~~](https://docs.siliconflow.cn/docs/model-names)

== iFlytek Spark Large Model

**API Interface Address** Selectable from the drop-down list in the software <del>`https://spark-api-open.xf-yun.com/v1`</del>

**API Key** Refer to the [official documentation](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E) to obtain the **APIKey** and **APISecret**, then fill in the format `APIKey:APISecret`.

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== Tencent Hunyuan Large Model

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.hunyuan.cloud.tencent.com/v1`</del>

**API Key** Refer to the [official documentation](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

== Baidu Qianfan Large Model

**API Interface Address** Selectable from the drop-down list in the software <del>`https://qianfan.baidubce.com/v2`</del>

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key** should be generated using Baidu Intelligent Cloud IAM's Access Key and Secret Key to create the BearerToken for the interface, or directly fill in the format `Access Key`:`Secret Key` in the **API Key** field. Note that this is not the API Key and Secret Key for the old v1 version of Qianfan ModelBuilder; they are not interchangeable.

== MiniMax

**API Interface Address** Selectable from the drop-down list in the software <del>`https://api.minimax.chat/v1`</del>

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

**model** Selectable from the drop-down list in the software [~~https://platform.minimaxi.com/document/Models?key=66701cb01d57f38758d581a4~~](https://platform.minimaxi.com/document/Models?key=66701cb01d57f38758d581a4)

:::