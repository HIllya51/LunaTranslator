# Giao diện dịch mô hình lớn

## Dịch Thuật Trực Tuyến Mô Hình Lớn

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

**API Key** https://platform.openai.com/api-keys

== Gemini

**API Key** https://aistudio.google.com/app/apikey

== Claude

**API Key** https://console.anthropic.com/

**model** https://docs.anthropic.com/en/docs/about-claude/models

== Cohere

**API Key** https://dashboard.cohere.com/api-keys

== x.ai

**API Key** https://console.x.ai/

== Groq

**API Key** https://console.groq.com/keys

== OpenRouter

**API Key** https://openrouter.ai/settings/keys

== Mistral AI

**API Key** https://console.mistral.ai/api-keys/

== Azure

**Địa Chỉ Giao Diện API** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

Thay thế `{endpoint}` và `{deployName}` bằng endpoint và deployName của bạn.

== Deepinfra

**API Key** https://deepinfra.com/dash/api_keys

== Cerebras

**API Key** https://cloud.cerebras.ai/  ->  API Keys

== Chutes

**API Key** https://chutes.ai/app/api


:::

### Giao Diện Mô Hình Lớn Trong Nước

::: tabs

== DeepSeek

**API Key** https://platform.deepseek.com/api_keys

== Alibaba Cloud Bailian Large Model

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== Động cơ Volcano của ByteDance

**API Key** [Tạo API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) để lấy.

**model** Sau khi [tạo điểm cuối suy luận](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10), điền vào **endpoint** thay vì **model**.

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

== Moonshot AI

**API Key** https://platform.moonshot.cn/console/api-keys

== Zhipu AI

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

== Lingyi Wanwu

**API Key** https://platform.lingyiwanwu.com/apikeys

== SiliconFlow

**API Key** https://cloud-hk.siliconflow.cn/account/ak

== iFlytek Spark Large Model

**API Key** Tham khảo [tài liệu chính thức](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E) để lấy **APIKey** và **APISecret**, sau đó điền theo định dạng `APIKey:APISecret`.

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== Tencent Hunyuan Large Model

**API Key** Tham khảo [tài liệu chính thức](https://cloud.tencent.com/document/product/1729/111008)

**model** https://cloud.tencent.com/document/product/1729/97731

== Baidu Qianfan Large Model

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key** nên được tạo bằng cách sử dụng Access Key và Secret Key của Baidu Intelligent Cloud IAM để tạo BearerToken cho giao diện, hoặc điền trực tiếp theo định dạng `Access Key`:`Secret Key` trong trường **API Key**. Lưu ý rằng đây không phải là API Key và Secret Key của phiên bản cũ v1 của Qianfan ModelBuilder; chúng không thể thay thế cho nhau.

== MiniMax

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

:::

## Dịch Ngoại Tuyến Mô Hình Lớn

### Giao Diện Chung Cho Mô Hình Lớn

Bạn cũng có thể sử dụng các công cụ như [llama.cpp](https://github.com/ggerganov/llama.cpp), [ollama](https://github.com/ollama/ollama), [one-api](https://github.com/songquanpeng/one-api) để triển khai các mô hình, sau đó điền địa chỉ và mô hình.

Bạn cũng có thể sử dụng các nền tảng như Kaggle để triển khai mô hình lên đám mây, trong trường hợp này bạn có thể cần sử dụng SECRET_KEY; nếu không, bạn có thể bỏ qua tham số SECRET_KEY.
