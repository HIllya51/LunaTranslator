# 大規模モデルAPI翻訳

::: details 複数のChatGPT互換インターフェース（または専用インターフェース）を同時に使用するには？
異なる複数のキーを使用してローテーションする場合は、単に|で区切るだけです。

しかし、異なるAPIインターフェースアドレス/prompt/model/パラメータなどを同時に使用して翻訳効果を比較したい場合は、次の方法を使用します。

右下の「+」ボタンをクリックします。
![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
ウィンドウが表示され、ChatGPT互換インターフェース（または専用インターフェース）を選択し、名前を付けます。これにより、現在のChatGPT互換インターフェース（または専用インターフェース）の設定とAPIが複製されます。
![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
複製されたインターフェースをアクティブにし、個別に設定できます。複製されたインターフェースは元のインターフェースと一緒に動作し、異なる設定を使用して動作させることができます。
![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)

:::

::: tip 
**model**はドロップダウンリストから選択でき、一部のインターフェースは**APIインターフェースアドレス**と**API Key**に基づいて動的にモデルリストを取得できます。これらの2つの項目を入力し、**model**の横にある更新ボタンをクリックすると、利用可能なモデルリストが取得されます。

プラットフォームがモデルリストの取得をサポートしていない場合、またはデフォルトリストに使用したいモデルがない場合は、インターフェースの公式ドキュメントを参照してモデルを手動で入力してください。
:::

## ChatGPT互換インターフェース

::: info
ほとんどの大規模モデルプラットフォームはChatGPT互換インターフェースを使用しています。

プラットフォームはさまざまであり、すべてを列挙することはできません。ここに記載されていないインターフェースについては、対応するパラメータを入力するためにそのドキュメントを参照してください。
::: 

#### 外国の大規模モデルインターフェース

::: tabs

== OpenAI

**APIインターフェースアドレス** `https://api.openai.com/v1` 

**API Key** https://platform.openai.com/api-keys

**model** https://platform.openai.com/docs/models

== x.ai

**APIインターフェースアドレス** `https://api.x.ai/`

**API Key** https://console.x.ai/

== groq

**APIインターフェースアドレス** `https://api.groq.com/openai/v1/chat/completions`

**API Key** https://console.groq.com/keys

**model** https://console.groq.com/docs/models `Model ID`を入力

== OpenRouter

**APIインターフェースアドレス** `https://openrouter.ai/api/v1/chat/completions`

**API Key** https://openrouter.ai/settings/keys

**model** https://openrouter.ai/docs/models

== Mistral AI

**APIインターフェースアドレス** `https://api.mistral.ai/v1/chat/completions`

**API Key** https://console.mistral.ai/api-keys/

**model** https://docs.mistral.ai/getting-started/models/

== Azure

**APIインターフェースアドレス** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

`{endpoint}`と`{deployName}`を自分のエンドポイントとデプロイ名に置き換えます。

== deepinfra

**APIインターフェースアドレス** `https://api.deepinfra.com/v1/openai/chat/completions` 

**API Key** https://deepinfra.com/dash/api_keys

== cerebras

**APIインターフェースアドレス** `https://api.cerebras.ai/v1/chat/completions` 

**model** `llama3.1-8b` `llama3.1-70b` `llama-3.3-70b` をサポート

**API Key** [https://inference.cerebras.ai](https://inference.cerebras.ai/)でモデルを選択し、任意のメッセージを送信した後、パケットをキャプチャして現在の`ヘッダー` -> `リクエストヘッダー` -> `Authorization`の値を確認します。これは`Bearer demo-xxxxhahaha`であり、その中の`demo-xxxxhahaha`がAPI Keyです。

![img](https://image.lunatranslator.org/zh/damoxing/cerebras.png) 

:::

#### 国内の大規模モデルインターフェース


::: tabs

== DeepSeek

**APIインターフェースアドレス** `https://api.deepseek.com`

**API Key** https://platform.deepseek.com/api_keys

**model** https://platform.deepseek.com/api-docs/zh-cn/pricing

== 阿里云百炼大模型

**APIインターフェースアドレス** `https://dashscope.aliyuncs.com/compatible-mode/v1`

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== 字节跳动豆包大模型

**APIインターフェースアドレス** `https://ark.cn-beijing.volces.com/api/v3`

**API Key** [API Keyの作成](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)から取得

**model** [推論エンドポイントの作成](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)後、**エンドポイント**を入力します。**モデル**ではありません。

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)


== 月之暗面

**APIインターフェースアドレス** `https://api.moonshot.cn`

**API Key** https://platform.moonshot.cn/console/api-keys

**model** https://platform.moonshot.cn/docs/intro

== 智谱AI

**APIインターフェースアドレス** `https://open.bigmodel.cn/api/paas/v4/chat/completions`

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

== 零一万物

**APIインターフェースアドレス** `https://api.lingyiwanwu.com`

**API Key** https://platform.lingyiwanwu.com/apikeys

**model** https://platform.lingyiwanwu.com/docs/api-reference#list-models
 
== 硅基流动

**APIインターフェースアドレス** `https://api.siliconflow.cn`

**API Key** https://cloud-hk.siliconflow.cn/account/ak

**model** https://docs.siliconflow.cn/docs/model-names

== 讯飞星火大模型

**APIインターフェースアドレス** `https://spark-api-open.xf-yun.com/v1`

**API Key** [公式ドキュメント](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)を参照して**APIKey**と**APISecret**を取得し、**APIKey:APISecret**の形式で入力します。

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== 腾讯混元大模型

**APIインターフェースアドレス** `https://api.hunyuan.cloud.tencent.com/v1`
<!-- 
**SecretId** & **SecretKey** https://console.cloud.tencent.com/cam/capi -->
**API Key** [公式ドキュメント](https://cloud.tencent.com/document/product/1729/111008)を参照

**model** https://cloud.tencent.com/document/product/1729/97731

== 百度千帆大模型

**APIインターフェースアドレス** `https://qianfan.baidubce.com/v2`

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
> **API Key**は、百度智能云IAMのAccess Key、Secret Keyを使用してインターフェースのBearerTokenを生成し、**API Key**として入力してください。または、`{Access Key}:{Secret Key}`の形式で両方を一緒に**API Key**に入力してください。注意：これは千帆ModelBuilderの旧版v1バージョンのAPI Key、Secret Keyではなく、互換性がありません。

:::

## 特定プラットフォームの専用インターフェース

::: info
一部の大規模モデルプラットフォームはChatGPTインターフェースと完全には互換性がありません。専用インターフェースにパラメータを入力して使用してください。
:::

::: tabs

== gemini

<a id="gemini"></a>

**APIインターフェースアドレス** `https://generativelanguage.googleapis.com`

**API Key** https://aistudio.google.com/app/apikey

**model** https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models


== claude

**APIインターフェースアドレス** `https://api.anthropic.com`

**API Key** https://console.anthropic.com/

**model**  https://docs.anthropic.com/en/docs/about-claude/models

== cohere

**API Key** https://dashboard.cohere.com/api-keys

**model** https://docs.cohere.com/docs/models

:::
