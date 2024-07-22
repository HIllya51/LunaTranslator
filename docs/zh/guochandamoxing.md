## 如何使用国产大模型API接口

## ChatGPT兼容接口


<!-- tabs:start -->

### **DeepSeek**

**API接口地址** `https://api.deepseek.com`

### **阿里云百炼大模型**


**API接口地址** `https://dashscope.aliyuncs.com/compatible-mode/v1`

### **字节跳动豆包大模型**



**API接口地址** `https://ark.cn-beijing.volces.com/api/v3`

**SECRET_KEY** 跟[官方文档](https://www.volcengine.com/docs/82379/1263279)获取

**model** 创建[推理接入点](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)后，填入**接入点**而非**模型**

![img](https://image.lunatranslator.xyz/zh/damoxing/doubao.png)


### **月之暗面**

**API接口地址** `https://api.moonshot.cn`

### **智谱AI**

**API接口地址** `https://open.bigmodel.cn/api/paas/v4/chat/completions`

### **零一万物**

**API接口地址** `https://api.lingyiwanwu.com`

### **硅基流动**

**API接口地址** `https://api.siliconflow.cn`

### **讯飞星火大模型**

**API接口地址** `https://spark-api-open.xf-yun.com/v1`

**SECRET_KEY** 参考[官方文档](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)获取**APIKey**和**APISecret**后，按照**APIKey:APISecret**的格式填入

<!-- tabs:end -->

<details>
  <summary>需要同时使用多个ChatGPT兼容接口？</summary>
  如果只是有多个不同的密钥想要轮询，只需用|分割就可以了。<br>
  但有时想要同时使用多个不同的api接口地址/prompt/model/参数等来对比翻译效果。方法是：<br>
  点击右下方的“+”按钮
  <img src="https://image.lunatranslator.xyz/zh/damoxing/extraapi1.png">
  弹出一个窗口，选择ChatGPT兼容接口，并为之取个名字。这样会复制一份当前ChatGPT兼容接口的设置和api。
  <img src="https://image.lunatranslator.xyz/zh/damoxing/extraapi2.png">
  激活复制的接口，并可以进行单独设置。复制的接口可以和原接口一起运行，从而使用多个不同的设置来运行。
  <img src="https://image.lunatranslator.xyz/zh/damoxing/extraapi3.png">
</details>


## 不兼容的专用接口

<!-- tabs:start -->

### **腾讯混元大模型**

略

### **百度千帆大模型**

!> 这个模型好像只支持中英翻译，不支持日文 

**model** 应填写百度接口文档中的**请求地址**的尾部，例如：

![img](https://image.lunatranslator.xyz/zh/damoxing/qianfan1.png)

![img](https://image.lunatranslator.xyz/zh/damoxing/qianfan2.png)

<!-- tabs:end -->


<details>
  <summary>推荐指数</summary>
  <table id="toupiao">
  </table> 
</details>