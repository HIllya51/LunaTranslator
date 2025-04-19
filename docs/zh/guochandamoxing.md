# 大模型在线翻译

::: details 同时使用多个大模型接口？
如果只是有多个不同的密钥想要轮询，只需用|分割就可以了。

但有时想要同时使用多个不同的api接口地址/prompt/model/参数等来对比翻译效果。方法是：

点击右下方的“+”按钮
![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
弹出一个窗口，选择大模型通用接口，并为之取个名字。这样会复制一份当前大模型通用接口的设置和api。
![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
激活复制的接口，并可以进行单独设置。复制的接口可以和原接口一起运行，从而使用多个不同的设置来运行。
![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: info
大部分**API接口地址**可以在下拉列表中选取，但可能会有遗漏。对于其他没有列举出来的接口，请自行查阅其文档来填写。
:::

::: tip
**model**可以在下拉列表中选取，且部分接口可以根据**API接口地址**和**API Key**动态获取模型列表，填好这两项后点击**model**旁的刷新按钮即可获取可用的模型列表。

如果平台不支持拉取模型的接口，且默认列表中没有要用的模型，那么请参照接口官方文档手动填写模型。
:::

### 外国大模型接口

::: tabs

== OpenAI

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.openai.com/v1`</del>

**API Key** https://platform.openai.com/api-keys

**model** 在软件内下拉列表中选取即可 [~~https://platform.openai.com/docs/models~~](https://platform.openai.com/docs/models)

== Gemini

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://generativelanguage.googleapis.com`</del>

**API Key** https://aistudio.google.com/app/apikey

**model** 在软件内下拉列表中选取即可 [~~https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models~~](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

== claude

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.anthropic.com/v1/messages`</del>

**API Key** https://console.anthropic.com/

**model**  https://docs.anthropic.com/en/docs/about-claude/models

== cohere

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.cohere.ai/compatibility/v1`</del>

**API Key** https://dashboard.cohere.com/api-keys

**model** 在软件内下拉列表中选取即可 [~~https://docs.cohere.com/docs/models~~](https://docs.cohere.com/docs/models)

== x.ai

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.x.ai/`</del>

**API Key** https://console.x.ai/

**model** 在软件内下拉列表中选取即可

== groq

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.groq.com/openai/v1/chat/completions`</del>

**API Key** https://console.groq.com/keys

**model** 在软件内下拉列表中选取即可 [~~https://console.groq.com/docs/models~~](https://console.groq.com/docs/models)

== OpenRouter

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://openrouter.ai/api/v1/chat/completions`</del>

**API Key** https://openrouter.ai/settings/keys

**model** 在软件内下拉列表中选取即可 [~~https://openrouter.ai/docs/models~~](https://openrouter.ai/docs/models)


== Mistral AI

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.mistral.ai/v1/chat/completions`</del>

**API Key** https://console.mistral.ai/api-keys/

**model** 在软件内下拉列表中选取即可 [~~https://docs.mistral.ai/getting-started/models/~~](https://docs.mistral.ai/getting-started/models/)

== Azure

**API接口地址** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

其中，将`{endpoint}`和`{deployName}`替换成你的endpoint和deployName

== deepinfra

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.deepinfra.com/v1/openai/chat/completions`</del>

**API Key** https://deepinfra.com/dash/api_keys

**model** 在软件内下拉列表中选取即可

== cerebras

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.cerebras.ai/v1/chat/completions`</del>

**API Key** https://cloud.cerebras.ai/  ->  API Keys

**model** 在软件内下拉列表中选取即可

:::

### 国产大模型接口

::: tabs

== DeepSeek

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.deepseek.com`</del>

**API Key** https://platform.deepseek.com/api_keys

**model** 在软件内下拉列表中选取即可 [~~https://api-docs.deepseek.com/zh-cn/quick_start/pricing~~](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)

== 阿里云百炼大模型

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://dashscope.aliyuncs.com/compatible-mode/v1`</del>

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== 字节跳动豆包大模型

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://ark.cn-beijing.volces.com/api/v3`</del>

**API Key** [创建API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)获取

**model** [创建推理接入点](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)后，填入**接入点**而非**模型**

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)


== 月之暗面

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.moonshot.cn`</del>

**API Key** https://platform.moonshot.cn/console/api-keys

**model** 在软件内下拉列表中选取即可 [~~https://platform.moonshot.cn/docs/intro~~](https://platform.moonshot.cn/docs/intro)

== 智谱AI

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://open.bigmodel.cn/api/paas/v4/chat/completions`</del>

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

== 零一万物

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.lingyiwanwu.com`</del>

**API Key** https://platform.lingyiwanwu.com/apikeys

**model** 在软件内下拉列表中选取即可 [~~https://platform.lingyiwanwu.com/docs/api-reference#list-models~~](https://platform.lingyiwanwu.com/docs/api-reference#list-models)

== 硅基流动

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.siliconflow.cn`</del>

**API Key** https://cloud-hk.siliconflow.cn/account/ak

**model** 在软件内下拉列表中选取即可 [~~https://docs.siliconflow.cn/docs/model-names~~](https://docs.siliconflow.cn/docs/model-names)

== 讯飞星火大模型

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://spark-api-open.xf-yun.com/v1`</del>

**API Key** 参考[官方文档](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)获取**APIKey**和**APISecret**后，按照**APIKey:APISecret**的格式填入

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== 腾讯混元大模型

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.hunyuan.cloud.tencent.com/v1`</del>
<!-- 
**SecretId** & **SecretKey** https://console.cloud.tencent.com/cam/capi -->
**API Key** 参考[官方文档](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

== 百度千帆大模型

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://qianfan.baidubce.com/v2`</del>

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key**请使用百度智能云IAM的Access Key、Secret Key来生成接口的BearerToken后作为**API Key**填入，或者按照`Access Key`:`Secret Key`的格式直接将两者一起填入**API Key**中。注意，不是千帆ModelBuilder的旧版v1版本接口的API Key、Secret Key，两者不能通用。

== MiniMax

**API接口地址** 在软件内下拉列表中选取即可 <del>`https://api.minimax.chat/v1`</del>

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

**model** 在软件内下拉列表中选取即可 [~~https://platform.minimaxi.com/document/Models?key=66701cb01d57f38758d581a4~~](https://platform.minimaxi.com/document/Models?key=66701cb01d57f38758d581a4)

:::
