# Large Model Translation Interface

## General Large Model Interface

::: details Using Multiple Large Model Interfaces Simultaneously?
If you only have multiple different keys and want to poll them, simply separate them with `|`.

However, sometimes you may want to use multiple different API interface addresses, prompts, models, or parameters simultaneously to compare translation results. Here's how:

1. Click the "+" button above and select the General Large Model Interface
   ![img](https://image.lunatranslator.org/zh/damoxing/plus.png)
1. A window will pop up - give it a name. This will duplicate the current settings and API of the General Large Model Interface
   ![img](https://image.lunatranslator.org/zh/damoxing/name.png)
1. Activate the duplicated interface and configure it separately. The duplicated interface can run alongside the original one, allowing you to use multiple different settings simultaneously.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

### Parameter Description  

1. #### API Endpoint  

    The `API endpoint` for most common large model platforms can be selected from the dropdown list, but some may be missing. For other endpoints not listed, please refer to the platform's documentation and fill them in manually.  

1. #### API Key  

    The `API Key` can be obtained from the platform. For multiple added keys, they will be automatically rotated, and their weights will be adjusted based on error feedback.  

1. #### Model  

    For most platforms, after filling in the `API endpoint` and `API Key`, clicking the refresh button next to `Model` will fetch the list of available models.  

    If the platform does not support pulling the model list, and the default list does not include the desired model, please manually enter the model name according to the official API documentation.  

1. #### Streaming Output  

    When enabled, the model's output will be displayed incrementally in a streaming manner. Otherwise, the entire output will be displayed at once after completion.  

1. #### Hide Thought Process  

    When enabled, content wrapped in `<think>` tags will not be displayed. If the thought process is hidden, the current thinking progress will still be shown.  

1. #### Number of Contextual Messages  

    A specified number of historical original and translated messages will be provided to the large model to improve translation. Setting this to 0 will disable this optimization.  

    - **Optimize Cache Hits** – For platforms like DeepSeek, the platform charges a lower price for cache-hit inputs. Enabling this will optimize the format of contextual messages to increase cache hit rates.  

1. #### Custom System Prompt / Custom User Message / Prefill  

    Different methods to control output content. You can configure them as preferred or use the defaults.  

    Custom system prompts and user messages can use fields to reference some information:
    - `{sentence}`: The text to be translated
    - `{srclang}` and `{tgtlang}`: Source language and target language. If only English is used in the prompt, they will be replaced with the English translation of the language names. Otherwise, they will be replaced with the translation of the language names in the current UI language.
    - `{contextOriginal[N]}` and `{contextTranslation[N]}` and `{contextTranslation[N]}`: N pieces of historical original text, translations, and both. N is unrelated to the "number of accompanying contexts" and should be replaced with an integer when input.
    - `{DictWithPrompt[XXXXX]}`: This field can reference entries from the "Proper Noun Translation" list. **If no matching entry is found, this field will be cleared to avoid disrupting the translation content**. Here, `XXXXX` is a prompt that guides the LLM to use the given entries for optimizing the translation. It can be customized, or you can disable custom user messages to use the default prompt.


1. #### Temperature / max tokens / top p / frequency penalty

    For certain models on some platforms, parameters like `top p` and `frequency penalty` may not be accepted by the interface, or the `max tokens` parameter may have been deprecated and replaced with `max completion tokens`. Activating or deactivating the switch can resolve these issues.

1. #### Reasoning Effort  

    For the Gemini platform, this option will automatically map to Gemini's `thinkingBudget`. The mapping rules are as follows:  
    
    minimal -> 0 (disable thinking, but not applicable to the Gemini-2.5-Pro model), low -> 512, medium -> -1 (enable dynamic thinking), high -> 24576.

1. #### Other Parameters  

    Only some common parameters are provided above. If the platform you are using offers other useful parameters not listed here, you can manually add key-value pairs.  

## Common Large Model Platforms

### Large-scale model platforms in Europe and America  

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

### Large-scale model platforms in China  

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

### API Aggregation Manager

You can also use API relay tools such as [new-api](https://github.com/QuantumNous/new-api) to more conveniently aggregate and manage multiple large model platform models and multiple keys.

For usage methods, you can refer to [this article](https://www.newapi.ai/en/docs/apps/luna-translator).

### Offline Deployment Model

You can also use tools like [llama.cpp](https://github.com/ggerganov/llama.cpp), [ollama](https://github.com/ollama/ollama) to deploy models, and then fill in the address and model.

