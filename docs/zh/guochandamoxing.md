## 如何使用大模型API翻译


<details>
  <summary>同时使用多个ChatGPT兼容接口（或专用接口）？</summary>
  如果只是有多个不同的密钥想要轮询，只需用|分割就可以了。<br>
  但有时想要同时使用多个不同的api接口地址/prompt/model/参数等来对比翻译效果。方法是：<br>
  点击右下方的“+”按钮
  <img src="https://image.lunatranslator.org/zh/damoxing/extraapi1.png">
  弹出一个窗口，选择ChatGPT兼容接口（或专用接口），并为之取个名字。这样会复制一份当前ChatGPT兼容接口（或专用接口）的设置和api。
  <img src="https://image.lunatranslator.org/zh/damoxing/extraapi2.png">
  激活复制的接口，并可以进行单独设置。复制的接口可以和原接口一起运行，从而使用多个不同的设置来运行。
  <img src="https://image.lunatranslator.org/zh/damoxing/extraapi3.png">
</details>

>**model**可以在下拉列表中选取，如果列表中没有也可以参照接口官方文档手动填写/修改。<br>
>部分接口可以根据**API接口地址**和**API Key**动态获取模型列表，填好这两项后点击**model**旁的刷新按钮即可获取可用的模型列表。


### ChatGPT兼容接口

>绝大多数大模型平台都是使用ChatGPT兼容接口。<br>由于平台各种各样，不可能一一列举。对于其他没有列举出来的接口，请自行查阅其文档来填写对应参数。

#### 外国大模型接口

<!-- tabs:start -->

### **OpenAI**

**API接口地址** `https://api.openai.com/v1` 

**API Key** https://platform.openai.com/api-keys

**model** https://platform.openai.com/docs/models

### **groq**

**API接口地址** `https://api.groq.com/openai/v1/chat/completions`

**API Key** https://console.groq.com/keys

**model** https://console.groq.com/docs/models 填写`Model ID`

### **OpenRouter**

**API接口地址** `https://openrouter.ai/api/v1/chat/completions`

**API Key** https://openrouter.ai/settings/keys

**model** https://openrouter.ai/docs/models

### **Mistral AI**

**API接口地址** `https://api.mistral.ai/v1/chat/completions`

**API Key** https://console.mistral.ai/api-keys/

**model** https://docs.mistral.ai/getting-started/models/

### **Azure**

**API接口地址** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

其中，将`{endpoint}`和`{deployName}`替换成你的endpoint和deployName

<!-- tabs:end -->

#### 国产大模型接口


<!-- tabs:start -->

### **DeepSeek**

**API接口地址** `https://api.deepseek.com`

**API Key** https://platform.deepseek.com/api_keys

**model** https://platform.deepseek.com/api-docs/zh-cn/pricing

### **阿里云百炼大模型**

**API接口地址** `https://dashscope.aliyuncs.com/compatible-mode/v1`

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

### **字节跳动豆包大模型**

**API接口地址** `https://ark.cn-beijing.volces.com/api/v3`

**API Key** [创建API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)获取

**model** [创建推理接入点](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)后，填入**接入点**而非**模型**

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)


### **月之暗面**

**API接口地址** `https://api.moonshot.cn`

**API Key** https://platform.moonshot.cn/console/api-keys

**model** https://platform.moonshot.cn/docs/intro

### **智谱AI**

**API接口地址** `https://open.bigmodel.cn/api/paas/v4/chat/completions`

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

### **零一万物**

**API接口地址** `https://api.lingyiwanwu.com`

**API Key** https://platform.lingyiwanwu.com/apikeys

**model** https://platform.lingyiwanwu.com/docs/api-reference#list-models
 
### **硅基流动**

**API接口地址** `https://api.siliconflow.cn`

**API Key** https://cloud-hk.siliconflow.cn/account/ak

**model** https://docs.siliconflow.cn/docs/model-names

### **讯飞星火大模型**

**API接口地址** `https://spark-api-open.xf-yun.com/v1`

**API Key** 参考[官方文档](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)获取**APIKey**和**APISecret**后，按照**APIKey:APISecret**的格式填入

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

<!-- tabs:end -->

### 特定平台的专用接口


>部分大模型平台不完全兼容ChatGPT接口，请在专用接口中填写参数使用。

#### 外国大模型接口


<!-- tabs:start -->

### **gemini**

**model** https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models

**API Key** https://aistudio.google.com/app/apikey

### **claude**

**BASE_URL** `https://api.anthropic.com`

**API_KEY** https://console.anthropic.com/

**model**  https://docs.anthropic.com/en/docs/about-claude/models

### **cohere**

**API Key** https://dashboard.cohere.com/api-keys

**model** https://docs.cohere.com/docs/models


<!-- tabs:end -->


#### 国产大模型接口

<!-- tabs:start -->

### **腾讯混元大模型**

**SecretId** & **SecretKey** https://console.cloud.tencent.com/cam/capi

**model** https://cloud.tencent.com/document/product/1729/97731

### **百度千帆大模型**

!> 这个模型好像只支持中英翻译，不支持日文 

**model** 应填写百度接口文档中的**请求地址**的尾部，例如：

![img](https://image.lunatranslator.org/zh/damoxing/qianfan1.png)

![img](https://image.lunatranslator.org/zh/damoxing/qianfan2.png)

<!-- tabs:end -->
