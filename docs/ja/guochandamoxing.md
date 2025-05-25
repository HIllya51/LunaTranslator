# 大規模モデル翻訳インターフェース

## 大規模モデルオンライン翻訳

::: details 複数の大規模モデルインターフェースを同時に使用するには？
異なる複数のキーをローテーションしたいだけなら、`|`で区切るだけでOKです。

しかし、複数の異なるAPIインターフェースアドレス、プロンプト、モデル、パラメータなどを同時に使用して翻訳効果を比較したい場合もあります。その方法は以下の通りです：

1. 上の「+」ボタンをクリックします。
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
1. ウィンドウがポップアップします。大規模モデルの汎用インターフェースを選択し、名前を付けます。これにより、現在の大規模モデル汎用インターフェースの設定とAPIが複製されます。
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
1. 複製されたインターフェースをアクティブにし、個別に設定できます。複製されたインターフェースは元のインターフェースと一緒に実行でき、複数の異なる設定を使用して実行できます。
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

**APIインターフェースアドレス** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

`{endpoint}`と`{deployName}`をあなたのendpointとdeployNameに置き換えてください。

== Deepinfra


**API Key** https://deepinfra.com/dash/api_keys

== Cerebras

**API Key** https://cloud.cerebras.ai/  ->  API Keys

== Chutes

**API Key** https://chutes.ai/app/api


:::

### 国内の大規模モデルインターフェース

::: tabs

== DeepSeek

**API Key** https://platform.deepseek.com/api_keys

== 阿里雲百煉大模型

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== バイトダンス ボルケーノエンジン

**API Key** [API Keyを作成](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)して取得

**model** [推論エンドポイントを作成](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)した後、**エンドポイント**を記入（**モデル**ではない）

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

== 月の暗面

**API Key** https://platform.moonshot.cn/console/api-keys

== 智譜AI

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

== 零一万物

**API Key** https://platform.lingyiwanwu.com/apikeys

== 硅基流動

**API Key** https://cloud-hk.siliconflow.cn/account/ak

== 訊飛星火大模型

**API Key** [公式ドキュメント](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)を参照して**APIKey**と**APISecret**を取得し、`APIKey:APISecret`の形式で記入

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== テンセント混元大模型

**API Key** [公式ドキュメント](https://cloud.tencent.com/document/product/1729/111008)を参照

**model** https://cloud.tencent.com/document/product/1729/97731

== 百度千帆大模型

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key**は、百度智能雲IAMのAccess KeyとSecret Keyを使用してインターフェースのBearerTokenを生成し、それを**API Key**として記入するか、`Access Key`:`Secret Key`の形式で直接記入してください。千帆ModelBuilderの旧版v1バージョンのAPI KeyとSecret Keyとは互換性がないので注意してください。

== MiniMax

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

:::

## 大規模モデルオフライン翻訳

### 大規模モデルの汎用インターフェース

[llama.cpp](https://github.com/ggerganov/llama.cpp)、[ollama](https://github.com/ollama/ollama)、[one-api](https://github.com/songquanpeng/one-api)などのツールを使用してモデルをデプロイし、アドレスとモデルを入力することができます。

Kaggleなどのプラットフォームを使用してモデルをクラウドにデプロイすることもできます。この場合、SECRET_KEYを使用する必要があるかもしれません。そうでなければ、SECRET_KEYパラメータを無視することができます。