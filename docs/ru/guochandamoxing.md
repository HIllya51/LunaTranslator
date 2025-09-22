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

### Описание параметров  

1. #### Адрес API-интерфейса  

    Большинство `адресов API-интерфейсов` распространённых платформ больших моделей можно выбрать из выпадающего списка, но некоторые могут отсутствовать. Для интерфейсов, которые не указаны в списке, пожалуйста, укажите их вручную, ознакомившись с документацией платформы.  

1. #### API Key  

    `API Key` можно получить на платформе. Если добавлено несколько ключей, система автоматически будет перебирать их по очереди и корректировать их приоритет на основе ошибок.  

1. #### model  

    Для большинства платформ после заполнения `адреса API-интерфейса` и `API Key` можно нажать кнопку обновления рядом с полем `model`, чтобы получить список доступных моделей.  

    Если платформа не поддерживает автоматическое получение списка моделей, а нужная модель отсутствует в списке по умолчанию, укажите её вручную, следуя официальной документации API.  

1. #### Потоковый вывод  

    При включении содержимое будет выводиться постепенно, по мере генерации модели. В противном случае весь текст отобразится только после завершения генерации.  

1. #### Скрывать процесс размышления  

    При включении содержимое, заключённое в теги \<think\>, отображаться не будет. Если скрытие процесса размышления активно, будет показываться текущий прогресс.  

1. #### Количество прикрепляемого контекста  

    Система будет прикреплять указанное количество предыдущих исходных текстов и переводов к запросу для улучшения качества перевода. Если установлено значение 0, эта функция отключается.  

    - **Оптимизация кэширования** — для таких платформ, как DeepSeek, запросы с попаданием в кэш тарифицируются по сниженной цене. Активация этой функции оптимизирует формат прикрепляемого контекста для увеличения вероятности попадания в кэш.  

1. #### Пользовательский system prompt / Пользовательское user message / prefill  

    Различные способы управления выводом модели. Можно настроить по своему усмотрению или оставить значения по умолчанию.  
        
    В пользовательских системных подсказках и сообщениях можно использовать поля для ссылок на некоторую информацию:
    - `{sentence}`: Текущий текст для перевода
    - `{srclang}` и `{tgtlang}`: Исходный язык и целевой язык. Если в подсказке используется только английский язык, они будут заменены на английский перевод названий языков. В противном случае они будут заменены на перевод названий языков на текущем языке интерфейса.
    - `{contextOriginal[N]}` и `{contextTranslation[N]}` и `{contextTranslation[N]}`: N элементов исторического текста, перевода и обоих. N не связано с «количеством сопроводительных контекстов» и должно быть заменено на целое число при вводе.
    - `{DictWithPrompt[XXXXX]}`: Это поле может ссылаться на записи из списка «Перевод собственных имен». **Если совпадающая запись не найдена, это поле будет очищено, чтобы не нарушать содержание перевода**. Здесь `XXXXX` — это промпт, который направляет LLM на использование данных записей для оптимизации перевода. Его можно настроить или отключить пользовательские сообщения для использования промпта по умолчанию.


1. #### Temperature / max tokens / top p / frequency penalty  

    Для некоторых моделей на некоторых платформах параметры, такие как `top p` и `frequency penalty`, могут не поддерживаться интерфейсом, или параметр `max tokens` может быть устаревшим и заменен на `max completion tokens`. Активирование или деактивирование переключателя может решить эти проблемы.

1. #### reasoning effort  

    Для платформы Gemini параметр автоматически преобразуется в `thinkingBudget` по следующим правилам:  
    
    минимальный -> 0 (отключение мышления, но не применимо к модели Gemini-2.5-Pro), низкий -> 512, средний -> -1 (включение динамического мышления), высокий -> 24576.

1. #### Другие параметры  

    Выше перечислены только основные параметры. Если платформа поддерживает другие полезные параметры, их можно добавить вручную в формате «ключ-значение».  

## Популярные платформы больших моделей

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

### Оффлайн большая модель

Также можно использовать такие инструменты как [llama.cpp](https://github.com/ggerganov/llama.cpp), [ollama](https://github.com/ollama/ollama), [new-api](https://github.com/QuantumNous/new-api) для развертывания модели, после чего ввести адрес и модель.

Иногда может потребоваться поделиться офлайн-развернутой моделью в сети, в этом случае может понадобиться SECRET_KEY. В остальное время можно игнорировать параметр SECRET_KEY.