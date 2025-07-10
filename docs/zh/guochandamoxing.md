# 大模型翻译接口

## 大模型通用接口

::: details 同时使用多个大模型接口？
如果只是有多个不同的密钥想要轮询，只需用|分割就可以了。

但有时想要同时使用多个不同的api接口地址/prompt/model/参数等来对比翻译效果。方法是：

1. 点击上方的“+”按钮
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
1. 弹出一个窗口，选择大模型通用接口，并为之取个名字。这样会复制一份当前大模型通用接口的设置和api。
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
1. 激活复制的接口，并可以进行单独设置。复制的接口可以和原接口一起运行，从而使用多个不同的设置来运行。
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: info
大部分**API接口地址**可以在下拉列表中选取，但可能会有遗漏。对于其他没有列举出来的接口，请自行查阅其文档来填写。
:::

::: tip
**model**可以在下拉列表中选取，且部分接口可以根据**API接口地址**和**API Key**动态获取模型列表，填好这两项后点击**model**旁的刷新按钮即可获取可用的模型列表。

如果平台不支持拉取模型的接口，且默认列表中没有要用的模型，那么请参照接口官方文档手动填写模型。
:::

### 欧美的大模型平台

::: tabs

== OpenAI

**API Key** https://platform.openai.com/api-keys

== Gemini

**API Key** https://aistudio.google.com/app/apikey

== claude

**API Key** https://console.anthropic.com/

**model**  https://docs.anthropic.com/en/docs/about-claude/models

== cohere

**API Key** https://dashboard.cohere.com/api-keys

== x.ai

**API Key** https://console.x.ai/

== groq

**API Key** https://console.groq.com/keys

== OpenRouter

**API Key** https://openrouter.ai/settings/keys


== Mistral AI

**API Key** https://console.mistral.ai/api-keys/

== Azure

**API接口地址** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

其中，将`{endpoint}`和`{deployName}`替换成你的endpoint和deployName

== deepinfra

**API Key** https://deepinfra.com/dash/api_keys

== cerebras

**API Key** https://cloud.cerebras.ai/  ->  API Keys

== Chutes

**API Key** https://chutes.ai/app/api

:::

### 中国的大模型平台

::: tabs

== DeepSeek

**API Key** https://platform.deepseek.com/api_keys

== 阿里云百炼大模型

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== 字节跳动火山引擎

**API Key** [创建API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)获取

**model** [创建推理接入点](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)后，填入**接入点**而非**模型**

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)


== 月之暗面

**API Key** https://platform.moonshot.cn/console/api-keys

== 智谱AI

**API Key** https://bigmodel.cn/usercenter/apikeys

== 零一万物

**API Key** https://platform.lingyiwanwu.com/apikeys

== 硅基流动

**API Key** https://cloud-hk.siliconflow.cn/account/ak

== 讯飞星火大模型

**API Key** 参考[官方文档](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)获取**APIKey**和**APISecret**后，按照**APIKey:APISecret**的格式填入

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== 腾讯混元大模型
<!-- 
**SecretId** & **SecretKey** https://console.cloud.tencent.com/cam/capi -->
**API Key** 参考[官方文档](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

== 百度千帆大模型

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key**请使用百度智能云IAM的Access Key、Secret Key来生成接口的BearerToken后作为**API Key**填入，或者按照`Access Key`:`Secret Key`的格式直接将两者一起填入**API Key**中。注意，不是千帆ModelBuilder的旧版v1版本接口的API Key、Secret Key，两者不能通用。

== MiniMax

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

:::

## 大模型通用接口 - 离线翻译

也可以使用[llama.cpp](https://github.com/ggerganov/llama.cpp) 、[ollama](https://github.com/ollama/ollama)、[one-api](https://github.com/songquanpeng/one-api)之类的工具进行模型的部署，然后将地址和模型填入。

也可以使用Kaggle之类的平台来把模型部署到云端，这时可能会需要用到SECRET_KEY，其他时候可以无视SECRET_KEY参数。

## Sakura大模型

::: tip
推荐使用，配置简单，效果好，也可以纯cpu运行轻量模型 
:::

部署方法可参考 https://github.com/SakuraLLM/SakuraLLM/wiki
