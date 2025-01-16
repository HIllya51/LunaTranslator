## 部署SakuraLLM到在线GPU平台

### 1. 设置内网穿透，以将请求转发给llama.cpp服务


注册[ngrok](https://ngrok.com/)，分别获取[NGROK_TOKEN](https://dashboard.ngrok.com/get-started/your-authtoken)和[NGROK_DOMAIN](https://dashboard.ngrok.com/cloud-edge/domains)，以供后面使用。

对于**Google Colab**，也可以不注册**ngrok**，将**NGROK_TOKEN**置为空，则会使用**gradio-tunneling**的随机域名进行内网穿透。

若使用**ngrok**，并填写了**NGROK_DOMAIN**，则每次运行时将会使用固定的域名进行内网穿透，否则将会使用随机的域名。

<details>
<summary>启动后，将会在log中看到本次运行的url接口地址，将url接口地址填写到翻译器中即可</summary>

  全空，使用gradio-tunneling，随机的域名
  <img src="https://image.lunatranslator.org/zh/sakurallm/tunnel.png">

  填写NGROK_TOKEN，使用ngrok，随机的域名
  
  <img src="https://image.lunatranslator.org/zh/sakurallm/tunnel3.png">
  
  
  填写NGROK_TOKEN+NGROK_DOMAIN，使用ngrok，固定的域名
  
  <img src="https://image.lunatranslator.org/zh/sakurallm/tunnel2.png">
</details>



### 2. 部署到在线GPU平台

::: tabs


== 飞桨Ai Studio

* 免费额度为每日登录领取4小时，并且可以通过一些积分任务获取更多时长

<details>
  <summary>1. 在<a href="https://aistudio.baidu.com/my/project/private" target="_blank">飞桨Ai Studio</a>中创建项目，注意<strong>项目框架</strong>必须为<strong>PaddlePaddle 3.0.0beta1</strong></summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle2.png">
</details>

<details>
  <summary>2. 点击<strong>启动环境</strong>，并选择<strong>V100 16GB</strong>。启动完毕后，进入环境</summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle3.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle4.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle5.png">
</details>

<details>
  <summary>3. 下载<a href="https://lunatranslator.org/nginxfile/aistudio.sakurallm.ipynb" target="_blank">ipynb脚本</a>，拖拽到文件区中以上传脚本，双击打开脚本。</summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle8.png">
</details>


<details>
  <summary>4. 设置ngrok密钥和域名，以及使用的模型</summary>
  将注册的ngrok的NGROK_TOKEN和NGROK_DOMAIN填入脚本中。
  REPO和MODEL是<code>https://huggingface.co/REPO</code>下的MODEL模型文件名
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle6.png">
</details>

<details>
  <summary>5. 运行脚本，等待模型下载，并获取内网穿透地址</summary>
  内网穿透地址在下面的log中可以看到。飞桨下载模型速度只有20MB/s，大概需要等待5分钟。
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle7.png">
</details>


<details>
  <summary>6. 运行结束后，回到项目详情中，主动停止项目，以避免消耗积分。</summary>
  再次启动环境时会保持之前的文件，直接从<strong>5</strong>继续开始即可，并且不需要再次下载模型。<br>
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle9.png">
</details>


== Google Colab

* 免费时长约为每天四小时，具体时长根据账号历史用量波动

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

:::
