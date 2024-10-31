## Как использовать API большой модели для перевода

<details>
  <summary>Использовать несколько совместимых с ChatGPT интерфейсов (или специальных интерфейсов) одновременно?</summary>
  Если у вас есть несколько разных ключей и вы хотите их ротацию, просто разделите их символом |.<br>
  Но иногда хочется использовать несколько разных адресов API/prompt/model/параметров и т.д. для сравнения результатов перевода. Метод следующий:<br>
  Нажмите кнопку "+" в правом нижнем углу
  <img src="https://image.lunatranslator.org/zh/damoxing/extraapi1.png">
  Появится окно, выберите совместимый с ChatGPT интерфейс (или специальный интерфейс) и дайте ему имя. Это скопирует текущие настройки и API совместимого с ChatGPT интерфейса (или специального интерфейса).
  <img src="https://image.lunatranslator.org/zh/damoxing/extraapi2.png">
  Активируйте скопированный интерфейс и можете настроить его отдельно. Скопированный интерфейс может работать вместе с исходным интерфейсом, что позволяет использовать несколько разных настроек.
  <img src="https://image.lunatranslator.org/zh/damoxing/extraapi3.png">
</details>

>**model** можно выбрать из выпадающего списка, если его нет в списке, можно ввести/изменить вручную, следуя официальной документации интерфейса.<br>
>Некоторые интерфейсы могут динамически получать список моделей на основе **адреса API** и **API Key**. После заполнения этих двух пунктов нажмите кнопку обновления рядом с **model**, чтобы получить список доступных моделей.

### Совместимый с ChatGPT интерфейс

>Большинство платформ больших моделей используют совместимый с ChatGPT интерфейс.<br>Из-за разнообразия платформ невозможно перечислить их все. Для других неперечисленных интерфейсов, пожалуйста, обратитесь к их документации, чтобы заполнить соответствующие параметры.

#### Зарубежные интерфейсы больших моделей

<!-- tabs:start -->

### **OpenAI**

**Адрес API** `https://api.openai.com/v1` 

**API Key** https://platform.openai.com/api-keys

**model** https://platform.openai.com/docs/models

### **groq**

**Адрес API** `https://api.groq.com/openai/v1/chat/completions`

**API Key** https://console.groq.com/keys

**model** https://console.groq.com/docs/models заполните `Model ID`

### **OpenRouter**

**Адрес API** `https://openrouter.ai/api/v1/chat/completions`

**API Key** https://openrouter.ai/settings/keys

**model** https://openrouter.ai/docs/models

### **Mistral AI**

**Адрес API** `https://api.mistral.ai/v1/chat/completions`

**API Key** https://console.mistral.ai/api-keys/

**model** https://docs.mistral.ai/getting-started/models/

### **Azure**

**Адрес API интерфейса** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

Замените `{endpoint}` и `{deployName}` на ваш endpoint и deployName.

### **DeepInfra**

**API Точка подключения** `https://api.deepinfra.com/v1/openai/chat/completions`

**API Ключ** **API Ключ должен быть установлен пустым, иначе произойдет ошибка.**

**Модель** Вы можете посмотреть доступные модели на [https://deepinfra.com/chat](https://deepinfra.com/chat). На момент написания этого документа, доступные бесплатные модели включают: `meta-llama/Meta-Llama-3.1-405B-Instruct` `meta-llama/Meta-Llama-3.1-70B-Instruct` `meta-llama/Meta-Llama-3.1-8B-Instruct` `mistralai/Mixtral-8x22B-Instruct-v0.1` `mistralai/Mixtral-8x7B-Instruct-v0.1` `microsoft/WizardLM-2-8x22B` `microsoft/WizardLM-2-7B` `Qwen/Qwen2.5-72B-Instruct` `Qwen/Qwen2-72B-Instruct` `Qwen/Qwen2-7B-Instruct` `microsoft/Phi-3-medium-4k-instruct` `google/gemma-2-27b-it` `openbmb/MiniCPM-Llama3-V-2_5` `mistralai/Mistral-7B-Instruct-v0.3` `lizpreciatior/lzlv_70b_fp16_hf` `openchat/openchat_3.5` `openchat/openchat-3.6-8b` `Phind/Phind-CodeLlama-34B-v2` `Gryphe/MythoMax-L2-13b` `cognitivecomputations/dolphin-2.9.1-llama-3-70b`

### **Cerebras**

**API Точка подключения** `https://api.cerebras.ai/v1/chat/completions`

**Модель** Поддерживает `llama3.1-8b` `llama3.1-70b`

**API Ключ** После выбора модели и отправки сообщения на [https://inference.cerebras.ai](https://inference.cerebras.ai/), вы можете перехватить запрос и проверить текущее значение `Заголовки` -> `Заголовки запроса` -> `Authorization`, которое будет `Bearer demo-xxxxhahaha`, где `demo-xxxxhahaha` является API Ключом.

![Ключ API Cerebras](https://image.lunatranslator.org/zh/damoxing/cerebras.png)

<!-- tabs:end -->

#### Китайские интерфейсы больших моделей

<!-- tabs:start -->

### **DeepSeek**

**Адрес API** `https://api.deepseek.com`

**API Key** https://platform.deepseek.com/api_keys

**model** https://platform.deepseek.com/api-docs/zh-cn/pricing

### **Alibaba Cloud Bailian Large Model**

**Адрес API** `https://dashscope.aliyuncs.com/compatible-mode/v1`

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

### **ByteDance Doubao Large Model**

**Адрес API** `https://ark.cn-beijing.volces.com/api/v3`

**API Key** [Создать API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) получить

**model** [Создать точку доступа для вывода](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10) затем заполните **точку доступа**, а не **модель**

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

### **Moonshot**

**Адрес API** `https://api.moonshot.cn`

**API Key** https://platform.moonshot.cn/console/api-keys

**model** https://platform.moonshot.cn/docs/intro

### **Zhipu AI**

**Адрес API** `https://open.bigmodel.cn/api/paas/v4/chat/completions`

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

### **Lingyi Wanwu**

**Адрес API** `https://api.lingyiwanwu.com`

**API Key** https://platform.lingyiwanwu.com/apikeys

**model** https://platform.lingyiwanwu.com/docs/api-reference#list-models

### **Siliconflow**

**Адрес API** `https://api.siliconflow.cn`

**API Key** https://cloud-hk.siliconflow.cn/account/ak

**model** https://docs.siliconflow.cn/docs/model-names

### **Xunfei Spark Large Model**

**Адрес API** `https://spark-api-open.xf-yun.com/v1`

**API Key** См. [официальную документацию](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E) получить **APIKey** и **APISecret**, затем заполните в формате **APIKey:APISecret**

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

### **Tencent Hunyuan Large Model**

**Адрес API** `https://api.hunyuan.cloud.tencent.com/v1`

**API Key** См. [официальную документацию](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

<!-- tabs:end -->

### Специальные интерфейсы для определенных платформ

>Некоторые платформы больших моделей не полностью совместимы с интерфейсом ChatGPT, пожалуйста, заполните параметры в специальном интерфейсе для использования.

<!-- tabs:start -->

### **gemini**

<a id="gemini"></a>

**Адрес API** `https://generativelanguage.googleapis.com`

**API Key** https://aistudio.google.com/app/apikey

**model** https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models

### **claude**

**Адрес API** `https://api.anthropic.com`

**API Key** https://console.anthropic.com/

**model**  https://docs.anthropic.com/en/docs/about-claude/models

### **cohere**

**API Key** https://dashboard.cohere.com/api-keys

**model** https://docs.cohere.com/docs/models

### **Baidu Qianfan Large Model**

!> Похоже, эта модель поддерживает только перевод с китайского на английский, не поддерживает японский 

**model** следует заполнить хвостовой частью **адреса запроса** в документации Baidu, например:

![img](https://image.lunatranslator.org/zh/damoxing/qianfan1.png)

![img](https://image.lunatranslator.org/zh/damoxing/qianfan2.png)

<!-- tabs:end -->