# Интерфейс перевода больших моделей

## Универсальный интерфейс для больших моделей

::: details Использование нескольких интерфейсов больших моделей одновременно？
Если вам нужно просто чередовать несколько разных ключей API, достаточно разделить их символом |.

Но иногда требуется одновременно использовать разные API-адреса/prompt/модели/параметры для сравнения результатов перевода. Метод следующий:

1. Нажмите кнопку "+" вверху
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
1. Появится окно, выберите "Универсальный интерфейс для больших моделей" и дайте ему имя. Это создаст копию текущих настроек и API универсального интерфейса.
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
1. Активируйте скопированный интерфейс и настройте его отдельно. Скопированный интерфейс может работать параллельно с оригинальным, позволяя использовать разные настройки.
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: info
Большинство **API-адресов** можно выбрать из выпадающего списка, но некоторые могут отсутствовать. Для интерфейсов, которых нет в списке, сверьтесь с их документацией и введите адрес вручную.
:::

::: tip
**Модель** можно выбрать из выпадающего списка. Некоторые интерфейсы позволяют динамически получать список моделей на основе **API-адреса** и **API Key** - заполните эти поля и нажмите кнопку обновления рядом с **model**, чтобы получить доступный список моделей.

Если платформа не поддерживает автоматическое получение списка моделей, и нужная модель отсутствует в списке по умолчанию, введите название модели вручную согласно официальной документации API.
:::

### Крупномасштабные платформы моделей в Европе и Америке  

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

**API-адрес** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions？api-version=2023-12-01-preview`

Замените `{endpoint}` и `{deployName}` на ваши значения endpoint и deployName

== deepinfra

**API Key** https://deepinfra.com/dash/api_keys

== cerebras

**API Key** https://cloud.cerebras.ai/  ->  API Keys

== Chutes

**API Key** https://chutes.ai/app/api

:::

### Крупномасштабные платформы моделей в Китае  

::: tabs

== DeepSeek

**API Key** https://platform.deepseek.com/api_keys

== Alibaba Cloud Bailian

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== ByteDance Volcano Engine

**API Key** Получите [создав API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey？apikey=%7B%7D)

**model** После [создания точки доступа для вывода](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint？current=1&pageSize=10) введите **точку доступа**, а не **модель**

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)


== Moon's Dark Side

**API Key** https://platform.moonshot.cn/console/api-keys

== Zhipu AI

**API Key** https://bigmodel.cn/usercenter/apikeys

== 01.AI

**API Key** https://platform.lingyiwanwu.com/apikeys

== SiliconFlow

**API Key** https://cloud-hk.siliconflow.cn/account/ak

== iFlytek Spark Large Model

**API Key** Ссылаясь на [официальную документацию](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E), получите **APIKey** и **APISecret**, затем введите в формате **APIKey:APISecret**

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== Tencent Hunyuan Large Model
<!-- 
**SecretId** & **SecretKey** https://console.cloud.tencent.com/cam/capi -->
**API Key** См. [официальную документацию](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

== Baidu Qianfan LLM

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key** Для заполнения **API Key** используйте Access Key и Secret Key из Baidu Intelligent Cloud IAM для генерации BearerToken интерфейса, либо введите их напрямую в **API Key** в формате `Access Key`:`Secret Key`. Обратите внимание, что это не API Key и Secret Key устаревшей версии v1 интерфейса Qianfan ModelBuilder - они не взаимозаменяемы.

== MiniMax

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

:::

## Универсальный интерфейс LLM - Оффлайн-перевод

Также можно использовать такие инструменты как [llama.cpp](https://github.com/ggerganov/llama.cpp), [ollama](https://github.com/ollama/ollama), [one-api](https://github.com/songquanpeng/one-api) для развертывания модели, после чего ввести адрес и модель.

也可以使用Kaggle之类的平台来把模型部署到云端，这时可能会需要用到SECRET_KEY，其他时候可以无视SECRET_KEY参数。
