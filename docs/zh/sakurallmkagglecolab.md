## 部署SakuraLLM到Kaggle/Google Colab

### 1. 注册[ngrok](https://ngrok.com/)，以将请求转发给llama.cpp服务

注册后，分别获取[NGROK_TOKEN](https://dashboard.ngrok.com/get-started/your-authtoken)和[NGROK_DOMAIN](https://dashboard.ngrok.com/cloud-edge/domains)，以供后面使用。

<details>
  <summary><strong>NGROK_TOKEN</strong></summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/ngrok2.png">
</details>

<details>
  <summary><strong>NGROK_DOMAIN</strong></summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/ngrok.png">
</details>

>之后，在Sakura大模型的设置中，将**API接口地址**填写为`https://`加上**NGROK_DOMAIN**即可，该地址不会发生变化。


### 2. 部署到Kaggle/Google Colab

<!-- tabs:start -->

### **Kaggle**

1. 注册<a href="https://kaggle.com/" target="_blank">Kaggle</a>，导入<a href="https://kaggle.com/kernels/welcome?src=https://lunatranslator.org/nginxfile/kaggle_sakurallm.ipynb" target="_blank">ipynb脚本</a>

<details>
  <summary>2. 选择GPU运行时，打开网络连接。首次使用需要验证手机号</summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/kaggle.2.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/kaggle.3.png">
</details>

<details>
  <summary>3. 设置ngrok密钥和域名，以及使用的模型</summary>
  将注册的ngrok的NGROK_TOKEN和NGROK_DOMAIN填入脚本中。<br>
  REPO和MODEL是<code>https://huggingface.co/REPO</code>下的MODEL模型文件名
  <img src="https://image.lunatranslator.org/zh/sakurallm/kaggle.png">
</details>

<details>
  <summary>4. 运行脚本，稍微等待一分钟左右即可</summary>
  llama.cpp是已经预先编译好的，省去了编译的时间，因此主要是下载模型需要花费一点时间。
  <img src="https://image.lunatranslator.org/zh/sakurallm/kagglerun.png">
</details>

### **Google Colab**


<details>
  <summary>1. 在Google drive中安装<strong>Colaboratory</strong>应用</summary>
  点击<strong>新建</strong>-><strong>更多</strong>-><strong>关联更多应用</strong>
  在应用市场中搜索<strong>Colaboratory</strong>安装即可
  <img src="https://image.lunatranslator.org/zh/sakurallm/installcolab.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/installcolab2.png">
</details>


<details>
  <summary>2. 打开<a href="https://colab.research.google.com/" target="_blank">Colab</a>，下载<a href="https://lunatranslator.org/nginxfile/kaggle_sakurallm.ipynb" target="_blank">ipynb脚本</a>并上传到Colab中。</summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab2.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab.png">
</details>

<details>
  <summary>3. 选择GPU运行时</summary>
  默认是使用CPU运行的，需要我们手动切换成T4 GPU运行。
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab5.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab4.png">
</details>

<details>
  <summary>4. 设置ngrok密钥和域名，以及使用的模型</summary>
  将注册的ngrok的NGROK_TOKEN和NGROK_DOMAIN填入脚本中。
  REPO和MODEL是<code>https://huggingface.co/REPO</code>下的MODEL模型文件名
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab3.png">
</details>

<details>
  <summary>5. 运行脚本，稍微等待一分钟左右即可</summary>
  llama.cpp是已经预先编译好的，省去了编译的时间，因此主要是下载模型需要花费一点时间。
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab6.png">
</details>

<!-- tabs:end -->
