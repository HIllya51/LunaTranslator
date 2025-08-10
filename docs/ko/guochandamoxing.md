# 대형 모델 번역 인터페이스

## 대형 모델 일반 인터페이스

::: details 여러 대형 모델 인터페이스를 동시에 사용하기？
단순히 여러 개의 다른 키를 번갈아 사용하려면 |로 구분하면 됩니다.

하지만 때로는 여러 개의 다른 API 인터페이스 주소/prompt/model/매개변수 등을 동시에 사용하여 번역 결과를 비교하고 싶을 수 있습니다. 방법은 다음과 같습니다:

1. 상단의 "+" 버튼을 클릭합니다
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
1. 팝업 창이 나타나면 대형 모델 일반 인터페이스를 선택하고 이름을 지정합니다. 이렇게 하면 현재 대형 모델 일반 인터페이스의 설정과 API가 복사됩니다.
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
1. 복사된 인터페이스를 활성화하고 개별적으로 설정할 수 있습니다. 복사된 인터페이스는 원본 인터페이스와 함께 실행될 수 있어 서로 다른 여러 설정으로 실행할 수 있습니다.
    ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

### 파라미터 설명  

1. #### API 인터페이스 주소  

    대부분의 일반적인 대형 모델 플랫폼의 **API 인터페이스 주소**는 드롭다운 목록에서 선택할 수 있지만, 누락된 경우가 있을 수 있습니다. 목록에 없는 인터페이스의 경우 플랫폼 문서를 참고하여 직접 입력해 주세요.  

1. #### API Key  

    **API Key**는 플랫폼에서 발급받을 수 있습니다. 여러 개의 Key를 추가하면 자동으로 순환하며, 오류 피드백에 따라 Key의 가중치를 조정합니다.  

1. #### model  

    대부분의 플랫폼에서는 **API 인터페이스 주소**와 **API Key**를 입력한 후 **model** 옆의 새로고침 버튼을 클릭하면 사용 가능한 모델 목록을 가져올 수 있습니다.  

    플랫폼이 모델 목록을 가져오는 인터페이스를 지원하지 않고, 기본 목록에 사용하려는 모델이 없는 경우, 인터페이스 공식 문서를 참고하여 모델을 수동으로 입력해 주세요.  

1. #### 스트리밍 출력  

    활성화하면 모델의 출력 내용을 증분 방식으로 스트리밍하며, 비활성화 시 모델이 완전히 출력한 후 모든 내용을 한 번에 표시합니다.  

1. #### 사고 과정 숨기기  

    활성화하면 \<think\> 태그로 감싼 내용을 표시하지 않습니다. 사고 과정 숨기기가 활성화된 경우 현재 사고 진행 상태를 표시합니다.  

1. #### 첨부할 컨텍스트 개수  

    이전의 원문과 번역을 몇 개까지 대형 모델에 제공하여 번역을 최적화합니다. 0으로 설정하면 이 최적화 기능이 비활성화됩니다.  

    - **캐시 적중률 최적화** — DeepSeek 등의 플랫폼에서는 캐시에 적중된 입력에 대해 더 낮은 가격으로 청구됩니다. 활성화하면 컨텍스트 첨부 방식을 최적화하여 캐시 적중률을 높입니다.  

1. #### 사용자 정의 system prompt / 사용자 정의 user message / prefill  

    출력 내용을 제어하는 여러 가지 방법으로, 선호에 따라 설정하거나 기본값을 사용할 수 있습니다.  

1. #### Temperature / max tokens / top p / frequency penalty  

    (생략)  

    - **max completion tokens 사용** — OpenAI 플랫폼에서 gpt-5 모델을 사용할 때, 인터페이스가 더 이상 max tokens 매개변수를 받지 않으므로 **max completion tokens 사용**을 활성화해야 합니다.  

1. #### reasoning effort  

    Gemini 플랫폼에서는 이 옵션을 Gemini의 thinkingBudget에 자동으로 매핑합니다. 매핑 규칙은 다음과 같습니다: 
    
    minimal→0(사고 비활성화, 단 Gemini-2.5-Pro 모델에는 적용되지 않음), low→512, medium→-1(동적 사고 활성화), high→24576.  

1. #### 기타 파라미터  

    위에서는 일반적인 파라미터만 제공했습니다. 사용 중인 플랫폼에서 다른 유용한 파라미터를 제공하는 경우 직접 키-값을 추가할 수 있습니다.  

## 일반적인 대형 모델 플랫폼

### 유럽과 미국의 대규모 모델 플랫폼  

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

**API 인터페이스 주소** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions？api-version=2023-12-01-preview`

여기서 `{endpoint}`와 `{deployName}`을 당신의 endpoint와 deployName으로 교체해 주세요.

== deepinfra

**API Key** https://deepinfra.com/dash/api_keys

== cerebras

**API Key** https://cloud.cerebras.ai/  ->  API Keys

== Chutes

**API Key** https://chutes.ai/app/api

:::

### 중국의 대규모 모델 플랫폼

::: tabs

== DeepSeek

**API Key** https://platform.deepseek.com/api_keys

== 알리바이둔 백련 대형 모델

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== 바이트댄스 화산 엔진

**API 키** [API 키 생성](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey？apikey=%7B%7D)에서 획득

**모델** [추론 엔드포인트 생성](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint？current=1&pageSize=10) 후, **모델**이 아닌 **엔드포인트**를 입력

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)


== 달의 어두운 면

**API Key** https://platform.moonshot.cn/console/api-keys

== 지푸AI

**API Key** https://bigmodel.cn/usercenter/apikeys

== 영일만물

**API Key** https://platform.lingyiwanwu.com/apikeys

== 실리콘 기반 흐름

**API Key** https://cloud-hk.siliconflow.cn/account/ak

== iFLYTEK 스파크 대형 모델

**API 키** [공식 문서](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E) 참조하여 **APIKey**와 **APISecret** 획득 후, **APIKey:APISecret** 형식으로 입력

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== 텐센트 혼위안 대형 모델
<!-- 
**SecretId** & **SecretKey** https://console.cloud.tencent.com/cam/capi -->
**API 키** [공식 문서](https://cloud.tencent.com/document/product/1729/111008) 참조

**model** https://cloud.tencent.com/document/product/1729/97731

== 바이두 첸판 대형 모델

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API 키** 바이두 스마트 클라우드 IAM의 Access Key, Secret Key를 사용하여 인터페이스의 BearerToken 생성 후 **API 키**로 입력하거나, `Access Key`:`Secret Key` 형식으로 직접 **API 키**에 함께 입력. 주의: 첸판 ModelBuilder의 구버전 v1 인터페이스 API Key, Secret Key와 혼용 불가.

== MiniMax

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

:::

### 오프라인 대형 모델 

[llama.cpp](https://github.com/ggerganov/llama.cpp), [ollama](https://github.com/ollama/ollama) 등의 도구를 사용하여 모델 배포 후 주소와 모델을 입력할 수도 있습니다.

也可以使用Kaggle之类的平台来把模型部署到云端，这时可能会需要用到SECRET_KEY，其他时候可以无视SECRET_KEY参数。
