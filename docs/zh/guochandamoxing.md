## 如何使用国产大模型API接口

## ChatGPT兼容接口

### DeepSeek

**API接口地址** `https://api.deepseek.com`

### 阿里云百炼大模型


**API接口地址** `https://dashscope.aliyuncs.com/compatible-mode/v1`

### 字节跳动豆包大模型等



**API接口地址** `https://ark.cn-beijing.volces.com/api/v3`

**SECRET_KEY** 跟[官方文档](https://www.volcengine.com/docs/82379/1263279)获取

**model** 创建[推理接入点](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)后，填入**接入点**而非**模型**

![img](https://image.lunatranslator.xyz/zh/damoxing/doubao.png)

## 不兼容的专用接口

### 腾讯混元大模型

略


### 百度千帆大模型

<div class="alert alert-warning" role="alert">
  <strong>警告：</strong> 这个模型好像只支持中英翻译，不支持日文
</div> 

**model** 应填写百度接口文档中的**请求地址**的尾部，例如：

![img](https://image.lunatranslator.xyz/zh/damoxing/qianfan1.png)

![img](https://image.lunatranslator.xyz/zh/damoxing/qianfan2.png)
