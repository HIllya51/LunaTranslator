# Dịch Thuật Trực Tuyến Mô Hình Lớn

::: details Sử Dụng Nhiều Giao Diện Mô Hình Lớn Đồng Thời?
Nếu bạn chỉ có nhiều khóa khác nhau và muốn luân phiên sử dụng chúng, chỉ cần tách chúng bằng `|`.

Tuy nhiên, đôi khi bạn có thể muốn sử dụng nhiều địa chỉ giao diện API, lời nhắc, mô hình hoặc tham số khác nhau đồng thời để so sánh kết quả dịch thuật. Đây là cách thực hiện:

1. Nhấp vào nút "+" ở góc dưới bên phải.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
2. Một cửa sổ sẽ xuất hiện. Chọn giao diện mô hình lớn chung và đặt tên cho nó. Điều này sẽ sao chép các cài đặt và API của giao diện mô hình lớn chung hiện tại.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
3. Kích hoạt giao diện đã sao chép và cấu hình nó riêng biệt. Giao diện đã sao chép có thể chạy song song với giao diện gốc, cho phép bạn sử dụng nhiều cài đặt khác nhau đồng thời.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

::: info
Hầu hết các **địa chỉ giao diện API** có thể được chọn từ danh sách thả xuống, nhưng một số có thể bị thiếu. Đối với các giao diện khác không có trong danh sách, vui lòng tham khảo tài liệu của chúng để điền thông tin chi tiết.
:::

::: tip
**model** có thể được chọn từ danh sách thả xuống, và một số giao diện có thể tự động lấy danh sách mô hình dựa trên **địa chỉ giao diện API** và **API Key**. Sau khi điền hai trường này, nhấp vào nút làm mới bên cạnh **model** để lấy danh sách mô hình khả dụng.

Nếu nền tảng không hỗ trợ lấy mô hình qua API và danh sách mặc định không bao gồm mô hình bạn cần, vui lòng tham khảo tài liệu chính thức của giao diện để điền thủ công mô hình.
:::

### Giao Diện Mô Hình Lớn Nước Ngoài

::: tabs

== OpenAI

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.openai.com/v1`</del>

**API Key** https://platform.openai.com/api-keys

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://platform.openai.com/docs/models~~](https://platform.openai.com/docs/models)

== Gemini

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://generativelanguage.googleapis.com`</del>

**API Key** https://aistudio.google.com/app/apikey

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models~~](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

== Claude

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.anthropic.com/v1/messages`</del>

**API Key** https://console.anthropic.com/

**model** https://docs.anthropic.com/en/docs/about-claude/models

== Cohere

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.cohere.ai/compatibility/v1`</del>

**API Key** https://dashboard.cohere.com/api-keys

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://docs.cohere.com/docs/models~~](https://docs.cohere.com/docs/models)

== x.ai

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.x.ai/`</del>

**API Key** https://console.x.ai/

**model** Có thể chọn từ danh sách thả xuống trong phần mềm

== Groq

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.groq.com/openai/v1/chat/completions`</del>

**API Key** https://console.groq.com/keys

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://console.groq.com/docs/models~~](https://console.groq.com/docs/models)

== OpenRouter

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://openrouter.ai/api/v1/chat/completions`</del>

**API Key** https://openrouter.ai/settings/keys

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://openrouter.ai/docs/models~~](https://openrouter.ai/docs/models)

== Mistral AI

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.mistral.ai/v1/chat/completions`</del>

**API Key** https://console.mistral.ai/api-keys/

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://docs.mistral.ai/getting-started/models/~~](https://docs.mistral.ai/getting-started/models/)

== Azure

**Địa Chỉ Giao Diện API** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

Thay thế `{endpoint}` và `{deployName}` bằng endpoint và deployName của bạn.

== Deepinfra

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.deepinfra.com/v1/openai/chat/completions`</del>

**API Key** https://deepinfra.com/dash/api_keys

**model** Có thể chọn từ danh sách thả xuống trong phần mềm

== Cerebras

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.cerebras.ai/v1/chat/completions`</del>

**API Key** https://cloud.cerebras.ai/  ->  API Keys

**model** Có thể chọn từ danh sách thả xuống trong phần mềm

:::

### Giao Diện Mô Hình Lớn Trong Nước

::: tabs

== DeepSeek

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.deepseek.com`</del>

**API Key** https://platform.deepseek.com/api_keys

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://api-docs.deepseek.com/zh-cn/quick_start/pricing~~](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)

== Alibaba Cloud Bailian Large Model

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://dashscope.aliyuncs.com/compatible-mode/v1`</del>

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== ByteDance Doubao Large Model

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://ark.cn-beijing.volces.com/api/v3`</del>

**API Key** [Tạo API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) để lấy.

**model** Sau khi [tạo điểm cuối suy luận](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10), điền vào **endpoint** thay vì **model**.

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

== Moonshot AI

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.moonshot.cn`</del>

**API Key** https://platform.moonshot.cn/console/api-keys

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://platform.moonshot.cn/docs/intro~~](https://platform.moonshot.cn/docs/intro)

== Zhipu AI

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://open.bigmodel.cn/api/paas/v4/chat/completions`</del>

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

== Lingyi Wanwu

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.lingyiwanwu.com`</del>

**API Key** https://platform.lingyiwanwu.com/apikeys

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://platform.lingyiwanwu.com/docs/api-reference#list-models~~](https://platform.lingyiwanwu.com/docs/api-reference#list-models)

== SiliconFlow

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.siliconflow.cn`</del>

**API Key** https://cloud-hk.siliconflow.cn/account/ak

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://docs.siliconflow.cn/docs/model-names~~](https://docs.siliconflow.cn/docs/model-names)

== iFlytek Spark Large Model

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://spark-api-open.xf-yun.com/v1`</del>

**API Key** Tham khảo [tài liệu chính thức](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E) để lấy **APIKey** và **APISecret**, sau đó điền theo định dạng `APIKey:APISecret`.

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== Tencent Hunyuan Large Model

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.hunyuan.cloud.tencent.com/v1`</del>

**API Key** Tham khảo [tài liệu chính thức](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

== Baidu Qianfan Large Model

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://qianfan.baidubce.com/v2`</del>

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key** nên được tạo bằng cách sử dụng Access Key và Secret Key của Baidu Intelligent Cloud IAM để tạo BearerToken cho giao diện, hoặc điền trực tiếp theo định dạng `Access Key`:`Secret Key` trong trường **API Key**. Lưu ý rằng đây không phải là API Key và Secret Key của phiên bản cũ v1 của Qianfan ModelBuilder; chúng không thể thay thế cho nhau.

== MiniMax

**Địa Chỉ Giao Diện API** Có thể chọn từ danh sách thả xuống trong phần mềm <del>`https://api.minimax.chat/v1`</del>

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

**model** Có thể chọn từ danh sách thả xuống trong phần mềm [~~https://platform.minimaxi.com/document/Models?key=66701cb01d57f38758d581a4~~](https://platform.minimaxi.com/document/Models?key=66701cb01d57f38758d581a4)

:::