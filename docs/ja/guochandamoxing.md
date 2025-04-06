# 大規模モデルオンライン翻訳

::: details 複数の大規模モデルインターフェースを同時に使用するには？
異なる複数のキーをローテーションしたいだけなら、`|`で区切るだけでOKです。

しかし、複数の異なるAPIインターフェースアドレス、プロンプト、モデル、パラメータなどを同時に使用して翻訳効果を比較したい場合もあります。その方法は以下の通りです：

1. 右下の「+」ボタンをクリックします。
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
2. ウィンドウがポップアップします。大規模モデルの汎用インターフェースを選択し、名前を付けます。これにより、現在の大規模モデル汎用インターフェースの設定とAPIが複製されます。
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
3. 複製されたインターフェースをアクティブにし、個別に設定できます。複製されたインターフェースは元のインターフェースと一緒に実行でき、複数の異なる設定を使用して実行できます。
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: info
ほとんどの**APIインターフェースアドレス**はドロップダウンリストから選択できますが、抜けている場合もあります。リストにない他のインターフェースについては、各自でドキュメントを参照して記入してください。
:::

::: tip
**model**はドロップダウンリストから選択でき、一部のインターフェースでは**APIインターフェースアドレス**と**API Key**に基づいてモデルリストを動的に取得できます。これら2つを入力した後、**model**の横にある更新ボタンをクリックすると、利用可能なモデルリストを取得できます。

プラットフォームがモデルを取得するAPIをサポートしておらず、デフォルトのリストに使用したいモデルがない場合は、インターフェースの公式ドキュメントを参照して手動でモデルを記入してください。
:::

### 外国の大規模モデルインターフェース

::: tabs

== OpenAI

**APIインターフェースアドレス** `https://api.openai.com/v1`

**API Key** https://platform.openai.com/api-keys

**model** https://platform.openai.com/docs/models

== Gemini

**APIインターフェースアドレス** `https://generativelanguage.googleapis.com`

**API Key** https://aistudio.google.com/app/apikey

**model** https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models

== Claude

**APIインターフェースアドレス** `https://api.anthropic.com/v1/messages`

**API Key** https://console.anthropic.com/

**model** https://docs.anthropic.com/en/docs/about-claude/models

== Cohere

**APIインターフェースアドレス** `https://api.cohere.ai/compatibility/v1`

**API Key** https://dashboard.cohere.com/api-keys

**model** https://docs.cohere.com/docs/models

== x.ai

**APIインターフェースアドレス** `https://api.x.ai/`

**API Key** https://console.x.ai/

== Groq

**APIインターフェースアドレス** `https://api.groq.com/openai/v1/chat/completions`

**API Key** https://console.groq.com/keys

**model** https://console.groq.com/docs/models `Model ID`を記入

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

`{endpoint}`と`{deployName}`をあなたのendpointとdeployNameに置き換えてください。

== Deepinfra

**APIインターフェースアドレス** `https://api.deepinfra.com/v1/openai/chat/completions`

**API Key** https://deepinfra.com/dash/api_keys

== Cerebras

**APIインターフェースアドレス** `https://api.cerebras.ai/v1/chat/completions`

**model** `llama3.1-8b`、`llama3.1-70b`、`llama-3.3-70b`をサポート

**API Key** [https://inference.cerebras.ai](https://inference.cerebras.ai/)でモデルを選択し、メッセージを送信した後、パケットキャプチャを行い、`ヘッダー` -> `リクエストヘッダー` -> `Authorization`の値を確認します。`Bearer demo-xxxxhahaha`という値のうち、`demo-xxxxhahaha`がAPI Keyです。

![img](https://image.lunatranslator.org/zh/damoxing/cerebras.png)

:::

### 国内の大規模モデルインターフェース

::: tabs

== DeepSeek

**APIインターフェースアドレス** `https://api.deepseek.com`

**API Key** https://platform.deepseek.com/api_keys

**model** https://platform.deepseek.com/api-docs/zh-cn/pricing

== 阿里雲百煉大模型

**APIインターフェースアドレス** `https://dashscope.aliyuncs.com/compatible-mode/v1`

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== 字節跳動豆包大模型

**APIインターフェースアドレス** `https://ark.cn-beijing.volces.com/api/v3`

**API Key** [API Keyを作成](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)して取得

**model** [推論エンドポイントを作成](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)した後、**エンドポイント**を記入（**モデル**ではない）

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

== 月の暗面

**APIインターフェースアドレス** `https://api.moonshot.cn`

**API Key** https://platform.moonshot.cn/console/api-keys

**model** https://platform.moonshot.cn/docs/intro

== 智譜AI

**APIインターフェースアドレス** `https://open.bigmodel.cn/api/paas/v4/chat/completions`

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

== 零一万物

**APIインターフェースアドレス** `https://api.lingyiwanwu.com`

**API Key** https://platform.lingyiwanwu.com/apikeys

**model** https://platform.lingyiwanwu.com/docs/api-reference#list-models

== 硅基流動

**APIインターフェースアドレス** `https://api.siliconflow.cn`

**API Key** https://cloud-hk.siliconflow.cn/account/ak

**model** https://docs.siliconflow.cn/docs/model-names

== 訊飛星火大模型

**APIインターフェースアドレス** `https://spark-api-open.xf-yun.com/v1`

**API Key** [公式ドキュメント](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)を参照して**APIKey**と**APISecret**を取得し、`APIKey:APISecret`の形式で記入

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== テンセント混元大模型

**APIインターフェースアドレス** `https://api.hunyuan.cloud.tencent.com/v1`

**API Key** [公式ドキュメント](https://cloud.tencent.com/document/product/1729/111008)を参照

**model** https://cloud.tencent.com/document/product/1729/97731

== 百度千帆大模型

**APIインターフェースアドレス** `https://qianfan.baidubce.com/v2`

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key**は、百度智能雲IAMのAccess KeyとSecret Keyを使用してインターフェースのBearerTokenを生成し、それを**API Key**として記入するか、`Access Key`:`Secret Key`の形式で直接記入してください。千帆ModelBuilderの旧版v1バージョンのAPI KeyとSecret Keyとは互換性がないので注意してください。

== MiniMax

**APIインターフェースアドレス** `https://api.minimax.chat/v1`

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

**model** https://platform.minimaxi.com/document/Models?key=66701cb01d57f38758d581a4

:::