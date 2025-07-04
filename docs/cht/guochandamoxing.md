# 大模型翻譯接口

## 大模型通用接口

::: details 同時使用多個大模型接口？
如果只是有多個不同的密鑰想要輪詢，只需用|分割就可以了。

但有時想要同時使用多個不同的api接口地址/prompt/model/參數等來對比翻譯效果。方法是：

1. 點擊上方的“+”按鈕
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
1. 彈出一個窗口，選擇大模型通用接口，併爲之取個名字。這樣會複製一份當前大模型通用接口的設置和api。
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
1. 激活複製的接口，並可以進行單獨設置。複製的接口可以和原接口一起運行，從而使用多個不同的設置來運行。
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: info
大部分**API接口地址**可以在下拉列表中選取，但可能會有遺漏。對於其他沒有列舉出來的接口，請自行查閱其文檔來填寫。
:::

::: tip
**model**可以在下拉列表中選取，且部分接口可以根據**API接口地址**和**API Key**動態獲取模型列表，填好這兩項後點擊**model**旁的刷新按鈕即可獲取可用的模型列表。

如果平臺不支持拉取模型的接口，且默認列表中沒有要用的模型，那麼請參照接口官方文檔手動填寫模型。
:::

### 外國大模型接口

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

其中，將`{endpoint}`和`{deployName}`替換成你的endpoint和deployName

== deepinfra

**API Key** https://deepinfra.com/dash/api_keys

== cerebras

**API Key** https://cloud.cerebras.ai/  ->  API Keys

== Chutes

**API Key** https://chutes.ai/app/api

:::

### 國產大模型接口

::: tabs

== DeepSeek

**API Key** https://platform.deepseek.com/api_keys

== 阿里雲百鍊大模型

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== 字節跳動火山引擎

**API Key** [創建API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)獲取

**model** [創建推理接入點](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)後，填入**接入點**而非**模型**

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)


== 月之暗面

**API Key** https://platform.moonshot.cn/console/api-keys

== 智譜AI

**API Key** https://bigmodel.cn/usercenter/apikeys

== 零一萬物

**API Key** https://platform.lingyiwanwu.com/apikeys

== 硅基流動

**API Key** https://cloud-hk.siliconflow.cn/account/ak

== 訊飛星火大模型

**API Key** 參考[官方文檔](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)獲取**APIKey**和**APISecret**後，按照**APIKey:APISecret**的格式填入

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== 騰訊混元大模型
<!-- 
**SecretId** & **SecretKey** https://console.cloud.tencent.com/cam/capi -->
**API Key** 參考[官方文檔](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

== 百度千帆大模型

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key**請使用百度智能雲IAM的Access Key、Secret Key來生成接口的BearerToken後作爲**API Key**填入，或者按照`Access Key`:`Secret Key`的格式直接將兩者一起填入**API Key**中。注意，不是千帆ModelBuilder的舊版v1版本接口的API Key、Secret Key，兩者不能通用。

== MiniMax

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

:::

## 大模型通用接口 - 離線翻譯

也可以使用[llama.cpp](https://github.com/ggerganov/llama.cpp) 、[ollama](https://github.com/ollama/ollama)、[one-api](https://github.com/songquanpeng/one-api)之類的工具進行模型的部署，然後將地址和模型填入。

也可以使用Kaggle之類的平臺來把模型部署到雲端，這時可能會需要用到SECRET_KEY，其他時候可以無視SECRET_KEY參數。

## Sakura大模型

::: tip
推薦使用，配置簡單，效果好，也可以純cpu運行輕量模型 
:::

部署方法可參考 https://github.com/SakuraLLM/SakuraLLM/wiki
