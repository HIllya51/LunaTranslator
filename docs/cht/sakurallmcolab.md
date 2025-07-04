## 部署SakuraLLM到在線GPU平臺

### 1. 設置內網穿透，以將請求轉發給llama.cpp服務


註冊[ngrok](https://ngrok.com/)，分別獲取[NGROK_TOKEN](https://dashboard.ngrok.com/get-started/your-authtoken)和[NGROK_DOMAIN](https://dashboard.ngrok.com/cloud-edge/domains)，以供後面使用。

對於**Google Colab**，也可以不註冊**ngrok**，將**NGROK_TOKEN**置爲空，則會使用**gradio-tunneling**的隨機域名進行內網穿透。

若使用**ngrok**，並填寫了**NGROK_DOMAIN**，則每次運行時將會使用固定的域名進行內網穿透，否則將會使用隨機的域名。

<details>
<summary>啓動後，將會在log中看到本次運行的url接口地址，將url接口地址填寫到翻譯器中即可</summary>

  全空，使用gradio-tunneling，隨機的域名
  <img src="https://image.lunatranslator.org/zh/sakurallm/tunnel.png">

  填寫NGROK_TOKEN，使用ngrok，隨機的域名
  
  <img src="https://image.lunatranslator.org/zh/sakurallm/tunnel3.png">
  
  
  填寫NGROK_TOKEN+NGROK_DOMAIN，使用ngrok，固定的域名
  
  <img src="https://image.lunatranslator.org/zh/sakurallm/tunnel2.png">
</details>



### 2. 部署到在線GPU平臺

::: tabs


== 飛槳Ai Studio

* 免費額度爲每日登錄領取4小時，並且可以通過一些積分任務獲取更多時長

<details>
  <summary>1. 在<a href="https://aistudio.baidu.com/my/project/private" target="_blank">飛槳Ai Studio</a>中創建項目，注意<strong>項目框架</strong>必須爲<strong>PaddlePaddle 3.0.0beta1</strong></summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle2.png">
</details>

<details>
  <summary>2. 點擊<strong>啓動環境</strong>，並選擇<strong>V100 16GB</strong>。啓動完畢後，進入環境</summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle3.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle4.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle5.png">
</details>

<details>
  <summary>3. 下載<a href="https://lunatranslator.org/nginxfile/aistudio.sakurallm.ipynb" target="_blank">ipynb腳本</a>，拖拽到文件區中以上傳腳本，雙擊打開腳本。</summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle8.png">
</details>


<details>
  <summary>4. 設置ngrok密鑰和域名，以及使用的模型</summary>
  將註冊的ngrok的NGROK_TOKEN和NGROK_DOMAIN填入腳本中。
  REPO和MODEL是<code>https://huggingface.co/REPO</code>下的MODEL模型文件名
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle6.png">
</details>

<details>
  <summary>5. 運行腳本，等待模型下載，並獲取內網穿透地址</summary>
  內網穿透地址在下面的log中可以看到。飛槳下載模型速度只有20MB/s，大概需要等待5分鐘。
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle7.png">
</details>


<details>
  <summary>6. 運行結束後，回到項目詳情中，主動停止項目，以避免消耗積分。</summary>
  再次啓動環境時會保持之前的文件，直接從<strong>5</strong>繼續開始即可，並且不需要再次下載模型。<br>
  <img src="https://image.lunatranslator.org/zh/sakurallm/paddle9.png">
</details>


== Google Colab

* 免費時長約爲每天四小時，具體時長根據賬號歷史用量波動

<details>
  <summary>1. 在Google drive中安裝<strong>Colaboratory</strong>應用</summary>
  點擊<strong>新建</strong>-><strong>更多</strong>-><strong>關聯更多應用</strong>
  在應用市場中搜索<strong>Colaboratory</strong>安裝即可
  <img src="https://image.lunatranslator.org/zh/sakurallm/installcolab.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/installcolab2.png">
</details>


<details>
  <summary>2. 打開<a href="https://colab.research.google.com/" target="_blank">Colab</a>，下載<a href="https://lunatranslator.org/nginxfile/kaggle_sakurallm.ipynb" target="_blank">ipynb腳本</a>並上傳到Colab中。</summary>
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab2.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab.png">
</details>

<details>
  <summary>3. 選擇GPU運行時</summary>
  默認是使用CPU運行的，需要我們手動切換成T4 GPU運行。
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab5.png">
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab4.png">
</details>

<details>
  <summary>4. 設置ngrok密鑰和域名，以及使用的模型</summary>
  將註冊的ngrok的NGROK_TOKEN和NGROK_DOMAIN填入腳本中。
  REPO和MODEL是<code>https://huggingface.co/REPO</code>下的MODEL模型文件名
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab3.png">
</details>

<details>
  <summary>5. 運行腳本，稍微等待一分鐘左右即可</summary>
  llama.cpp是已經預先編譯好的，省去了編譯的時間，因此主要是下載模型需要花費一點時間。
  <img src="https://image.lunatranslator.org/zh/sakurallm/colab6.png">
</details>

:::
