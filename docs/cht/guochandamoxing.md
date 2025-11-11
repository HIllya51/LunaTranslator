# 大模型翻譯介面

## 大模型通用介面

::: details 同時使用多個大模型介面？
如果只是有多個不同的金鑰想要輪詢，只需用`|`分割就可以了。

但有時想要同時使用多個不同的 API 介面位址／Prompt／Model／參數等來對比翻譯效果。方法是：

1. 點擊上方的「+」按鈕，選擇大模型通用接口
    ![img](https://image.lunatranslator.org/zh/damoxing/plus.png)
1. 彈出一個視窗，為之取個名字。這樣會複製一份當前大模型通用接口的設定和API
    ![img](https://image.lunatranslator.org/zh/damoxing/name.png)
1. 啟用複製的介面，並可以進行單獨設定。複製的介面可以和原介面一起執行，從而使用多個不同的設定來執行。
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

### 參數說明

1. #### API 介面位址

    大部份常見大模型平台的`API 介面位址`可以在下拉選單中選取，但可能會有遺漏。對於其他沒有列舉出來的介面，請自行查閱平台的文件來填寫。

1. #### API Key

    `API Key`可以在平台取得。對於新增的多個 Key，會自動進行輪詢，並根據錯誤回饋調整 Key 的權重。

1. #### Model

    大部份平台填寫好`API 介面位址`和`API Key`後，點擊`model`旁的重新整理按鈕即可取得可用的模型清單。

    如果平台不支援取得模型清單的介面，或預設清單中沒有要用的模型時，那麼請參照介面官方文件手動填寫模型。

1. #### 流式輸出

    啟用後，將以流式逐漸顯示模型輸出的內容，否則會在模型完整輸出後一次性顯示所有內容。

1. #### 隱藏思考過程

    啟用後將不顯示`<think>`標籤包裹的內容。若啟用了隱藏思考過程，會顯示目前的思考進度。

1. #### 附帶上下文個數

    會附帶若干筆歷史的原文和翻譯介面提供給大模型，以優化翻譯。設定為`0`將停用此優化。

    - **優化快取命中** - 對於 DeepSeek 等平台，平台會對快取命中的輸入以更低的價格計費。啟用後會優化附帶上下文時的形式以增加快取命中率。

1. #### 自訂 System Prompt／自訂 User Message／Prefill

    幾種不同的控制輸出內容的手段，可以根據喜好設定，或者使用預設即可。

    自訂 System Prompt 和 User Message 中可以使用變數來引用一些訊息：
    - `{sentence}`：目前欲翻譯的文字。
    - `{srclang}`和`{tgtlang}`：來源語言和目標語言。如果 Prompt 中僅使用英文，則會取代成語言名稱的英文翻譯，否則會取代成語言名稱的目前 UI 語言翻譯。
    - `{contextOriginal[N]}`和`{contextTranslation[N]}`和`{contextTranslation[N]}`：`N`筆歷史原文、譯文、兩者。`N`與「附帶上下文個數」無關，輸入時需替換成整數。
    - `{DictWithPrompt[XXXXX]}`：此欄位可以引用「專有名詞翻譯」清單中的詞條。**當沒有匹配到的詞條時，該欄位會被清除以避免破壞翻譯內容**。其中，`XXXXX`是一段引導LLM使用給定的詞條來最佳化翻譯的提示，可以自行定義，或停用自訂使用者訊息以使用預設的提示。

1. #### Temperature／Max Tokens／Top P／Frequency Penalty

    對於部份平台的部份模型，可能`top p`和`frequency penalty`等參數不被介面接受，或者`max tokens`參數被廢棄並改為`max completion tokens`。啟用或停用開關可以解決這些問題。

1. #### reasoning effort

    對於 Gemini 平台，會自動將選項映射為 Gemini 的`thinkingBudget`，映射規則為：

    `minimal`->`0`（停用思考，但對於 Gemini-2.5-Pro 模型不適用）；`low`->`512`；`medium`->`-1`（啟用動態思維）；`high`->`24576`。

1. #### 其他參數

    以上只提供了一些常見的參數，如果使用的平台提供了其他未列出的有用的參數，可以自行新增鍵值。

## 常見的大模型平台

### 歐美的大模型平台

::: tabs

== OpenAI

**API Key** https://platform.openai.com/api-keys

== Gemini

**API Key** https://aistudio.google.com/app/apikey

== claude

**API Key** https://console.anthropic.com/

**Model**  https://docs.anthropic.com/en/docs/about-claude/models

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

**API 介面位址** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

其中，將`{endpoint}`和`{deployName}`取代成你的 Endpoint 和 DeployName

== deepinfra

**API Key** https://deepinfra.com/dash/api_keys

== cerebras

**API Key** https://cloud.cerebras.ai/  ->  API Keys

== Chutes

**API Key** https://chutes.ai/app/api

:::

### 中國的大模型平台

::: tabs

== DeepSeek

**API Key** https://platform.deepseek.com/api_keys

== 阿里雲百煉大模型

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**Model** https://help.aliyun.com/zh/model-studio/getting-started/models

== 字節跳動火山引擎

**API Key** [建立 API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) 取得

**Model** [建立推理接入點](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)後，填入**接入點**而非**模型**

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)


== 月之暗面

**API Key** https://platform.moonshot.cn/console/api-keys

== 智譜 AI

**API Key** https://bigmodel.cn/usercenter/apikeys

== 零一萬物

**API Key** https://platform.lingyiwanwu.com/apikeys

== 矽基流動

**API Key** https://cloud-hk.siliconflow.cn/account/ak

== 訊飛星火大模型

**API Key** 參考[官方文件](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)取得 **APIKey** 和 **APISecret** 後，按照 **APIKey:APISecret** 的格式填入

**Model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== 騰訊混元大模型
<!-- 
**SecretId** & **SecretKey** https://console.cloud.tencent.com/cam/capi -->
**API Key** 參考[官方文件](https://cloud.tencent.com/document/product/1729/111008)

**Model** https://cloud.tencent.com/document/product/1729/97731

== 百度千帆大模型

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**Model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key** 請使用百度智能雲 IAM 的 Access Key、Secret Key 來生成介面的 BearerToken 後作為 **API Key** 填入，或者按照`Access Key`:`Secret Key`的格式直接將兩者一起填入 **API Key** 中。注意，不是千帆 ModelBuilder 的舊版 v1 版本介面的 API Key、Secret Key，兩者不能通用。

== MiniMax

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

:::

### API 聚合管理器

也可以使用[new-api](https://github.com/QuantumNous/new-api)等API中繼工具，更方便地聚合管理多種大模型平台模型和多個金鑰。

使用方法可以參考[此文章](https://www.newapi.ai/apps/luna-translator/).


### 离线部署模型

可以使用 [llama.cpp](https://github.com/ggerganov/llama.cpp)、[Ollama](https://github.com/ollama/ollama) 之類的工具進行模型的部署，然後將位址和模型填入。


#### Sakura 大模型

部署方法可參考：https://github.com/SakuraLLM/SakuraLLM/wiki
