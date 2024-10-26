## Другие API больших моделей

### **DeepInfra**

**API Точка подключения** `https://api.deepinfra.com/v1/openai/chat/completions`

**API Ключ** **API Ключ должен быть установлен пустым, иначе произойдет ошибка.**

**Модель** Вы можете посмотреть доступные модели на [https://deepinfra.com/chat](https://deepinfra.com/chat). На момент написания этого документа, доступные бесплатные модели включают: `meta-llama/Meta-Llama-3.1-405B-Instruct` `meta-llama/Meta-Llama-3.1-70B-Instruct` `meta-llama/Meta-Llama-3.1-8B-Instruct` `mistralai/Mixtral-8x22B-Instruct-v0.1` `mistralai/Mixtral-8x7B-Instruct-v0.1` `microsoft/WizardLM-2-8x22B` `microsoft/WizardLM-2-7B` `Qwen/Qwen2.5-72B-Instruct` `Qwen/Qwen2-72B-Instruct` `Qwen/Qwen2-7B-Instruct` `microsoft/Phi-3-medium-4k-instruct` `google/gemma-2-27b-it` `openbmb/MiniCPM-Llama3-V-2_5` `mistralai/Mistral-7B-Instruct-v0.3` `lizpreciatior/lzlv_70b_fp16_hf` `openchat/openchat_3.5` `openchat/openchat-3.6-8b` `Phind/Phind-CodeLlama-34B-v2` `Gryphe/MythoMax-L2-13b` `cognitivecomputations/dolphin-2.9.1-llama-3-70b`

### **Cerebras**

**API Точка подключения** `https://api.cerebras.ai/v1/chat/completions`

**Модель** Поддерживает `llama3.1-8b` `llama3.1-70b`

**API Ключ** После выбора модели и отправки сообщения на [https://inference.cerebras.ai](https://inference.cerebras.ai/), вы можете перехватить запрос и проверить текущее значение `Заголовки` -> `Заголовки запроса` -> `Authorization`, которое будет `Bearer demo-xxxxhahaha`, где `demo-xxxxhahaha` является API Ключом.

![Ключ API Cerebras](https://image.lunatranslator.org/zh/damoxing/cerebras.png)