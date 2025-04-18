# Dịch thuật trực tuyến bằng mô hình lớn

::: details Sử dụng nhiều giao diện mô hình lớn cùng lúc?
Nếu bạn chỉ có nhiều khóa khác nhau và muốn luân phiên sử dụng chúng, chỉ cần ngăn cách chúng bằng ký hiệu `|`.

Tuy nhiên, đôi khi bạn có thể muốn sử dụng nhiều địa chỉ giao diện API, lời nhắc, mô hình hoặc tham số khác nhau cùng lúc để so sánh kết quả dịch. Đây là cách thực hiện:

1. Nhấp vào nút "+" ở góc dưới bên phải.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
2. Một cửa sổ sẽ xuất hiện. Chọn giao diện mô hình lớn chung và đặt tên cho nó. Điều này sẽ sao chép các cài đặt và API hiện tại của giao diện mô hình lớn chung.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
3. Kích hoạt giao diện đã sao chép và cấu hình nó riêng biệt. Giao diện đã sao chép có thể chạy song song với giao diện ban đầu, cho phép bạn sử dụng nhiều cài đặt khác nhau cùng lúc.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: info
Hầu hết **địa chỉ giao diện API** có thể được chọn từ danh sách thả xuống, nhưng một số có thể bị thiếu. Đối với các giao diện khác không được liệt kê, vui lòng tham khảo tài liệu của chúng để điền chi tiết.
:::

::: tip
**Mô hình** có thể được chọn từ danh sách thả xuống, và một số giao diện có thể tự động lấy danh sách mô hình dựa trên **địa chỉ giao diện API** và **Khóa API**. Sau khi điền hai trường này, nhấp vào nút làm mới bên cạnh **mô hình** để lấy danh sách mô hình khả dụng.

Nếu nền tảng không hỗ trợ việc lấy mô hình qua API và danh sách mặc định không bao gồm mô hình bạn cần, vui lòng tham khảo tài liệu chính thức của giao diện để điền thủ công mô hình.
:::

### Giao diện mô hình lớn nước ngoài

::: tabs

== OpenAI

**Địa chỉ giao diện API** `https://api.openai.com/v1`

**Khóa API** https://platform.openai.com/api-keys

**Mô hình** https://platform.openai.com/docs/models

== Gemini

**Địa chỉ giao diện API** `https://generativelanguage.googleapis.com`

**Khóa API** https://aistudio.google.com/app/apikey

**Mô hình** https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models

== Claude

**Địa chỉ giao diện API** `https://api.anthropic.com/v1/messages`

**Khóa API** https://console.anthropic.com/

**Mô hình** https://docs.anthropic.com/en/docs/about-claude/models

== Cohere

**Địa chỉ giao diện API** `https://api.cohere.ai/compatibility/v1`

**Khóa API** https://dashboard.cohere.com/api-keys

**Mô hình** https://docs.cohere.com/docs/models

== x.ai

**Địa chỉ giao diện API** `https://api.x.ai/`

**Khóa API** https://console.x.ai/

== Groq

**Địa chỉ giao diện API** `https://api.groq.com/openai/v1/chat/completions`

**Khóa API** https://console.groq.com/keys

**Mô hình** https://console.groq.com/docs/models Điền vào `ID mô hình`

== OpenRouter

**Địa chỉ giao diện API** `https://openrouter.ai/api/v1/chat/completions`

**Khóa API** https://openrouter.ai/settings/keys

**Mô hình** https://openrouter.ai/docs/models

== Mistral AI

**Địa chỉ giao diện API** `https://api.mistral.ai/v1/chat/completions`

**Khóa API** https://console.mistral.ai/api-keys/

**Mô hình** https://docs.mistral.ai/getting-started/models/

== Azure

**Địa chỉ giao diện API** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

Thay thế `{endpoint}` và `{deployName}` bằng điểm cuối và tên triển khai của bạn.

== Deepinfra

**Địa chỉ giao diện API** `https://api.deepinfra.com/v1/openai/chat/completions`

**Khóa API** https://deepinfra.com/dash/api_keys

== Cerebras

**Địa chỉ giao diện API** `https://api.cerebras.ai/v1/chat/completions`

**Mô hình** Hỗ trợ `llama3.1-8b`, `llama3.1-70b`, `llama-3.3-70b`

**Khóa API** https://cloud.cerebras.ai/  ->  API Keys

:::

### Giao diện mô hình lớn trong nước

::: tabs

== DeepSeek

**Địa chỉ giao diện API** `https://api.deepseek.com`

**Khóa API** https://platform.deepseek.com/api_keys

**Mô hình** https://platform.deepseek.com/api-docs/zh-cn/pricing

== Mô hình lớn Bailian của Alibaba Cloud

**Địa chỉ giao diện API** `https://dashscope.aliyuncs.com/compatible-mode/v1`

**Khóa API** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**Mô hình** https://help.aliyun.com/zh/model-studio/getting-started/models

== Mô hình lớn Doubao của ByteDance

**Địa chỉ giao diện API** `https://ark.cn-beijing.volces.com/api/v3`

**Khóa API** [Tạo khóa API](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) để lấy.

**Mô hình** Sau khi [tạo điểm cuối suy luận](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10), điền vào **điểm cuối** thay vì **mô hình**.

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

== Moonshot AI

**Địa chỉ giao diện API** `https://api.moonshot.cn`

**Khóa API** https://platform.moonshot.cn/console/api-keys

**Mô hình** https://platform.moonshot.cn/docs/intro

== Zhipu AI

**Địa chỉ giao diện API** `https://open.bigmodel.cn/api/paas/v4/chat/completions`

**Khóa API** https://bigmodel.cn/usercenter/apikeys

**Mô hình** https://bigmodel.cn/dev/howuse/model

== Lingyi Wanwu

**Địa chỉ giao diện API** `https://api.lingyiwanwu.com`

**Khóa API** https://platform.lingyiwanwu.com/apikeys

**Mô hình** https://platform.lingyiwanwu.com/docs/api-reference#list-models

== SiliconFlow

**Địa chỉ giao diện API** `https://api.siliconflow.cn`

**Khóa API** https://cloud-hk.siliconflow.cn/account/ak

**Mô hình** https://docs.siliconflow.cn/docs/model-names

== Mô hình lớn Spark của iFlytek

**Địa chỉ giao diện API** `https://spark-api-open.xf-yun.com/v1`

**Khóa API** Tham khảo [tài liệu chính thức](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E) để lấy **APIKey** và **APISecret**, sau đó điền theo định dạng `APIKey:APISecret`.

**Mô hình** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== Mô hình lớn Hunyuan của Tencent

**Địa chỉ giao diện API** `https://api.hunyuan.cloud.tencent.com/v1`

**Khóa API** Tham khảo [tài liệu chính thức](https://cloud.tencent.com/document/product/1729/111008)

**Mô hình** https://cloud.tencent.com/document/product/1729/97731

== Mô hình lớn Qianfan của Baidu

**Địa chỉ giao diện API** `https://qianfan.baidubce.com/v2`

**Khóa API** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**Mô hình** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**Khóa API** nên được tạo bằng cách sử dụng Khóa truy cập và Khóa bí mật của IAM Baidu Intelligent Cloud để tạo BearerToken cho giao diện, hoặc trực tiếp điền theo định dạng `Khóa truy cập`:`Khóa bí mật` vào trường **Khóa API**. Lưu ý rằng đây không phải là Khóa API và Khóa bí mật cho phiên bản v1 cũ của Qianfan ModelBuilder; chúng không thể thay thế cho nhau.

== MiniMax

**Địa chỉ giao diện API** `https://api.minimax.chat/v1`

**Khóa API** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

**Mô hình** https://platform.minimaxi.com/document/Models?key=66701cb01d57f38758d581a4

:::