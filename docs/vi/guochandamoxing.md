# Giao diện dịch mô hình lớn

## Giao Diện Chung Cho Mô Hình Lớn

::: details Sử Dụng Nhiều Giao Diện Mô Hình Lớn Đồng Thời?
Nếu bạn chỉ có nhiều khóa khác nhau và muốn luân phiên sử dụng chúng, chỉ cần tách chúng bằng `|`.

Tuy nhiên, đôi khi bạn có thể muốn sử dụng nhiều địa chỉ giao diện API, lời nhắc, mô hình hoặc tham số khác nhau đồng thời để so sánh kết quả dịch thuật. Đây là cách thực hiện:

1. Nhấp vào nút "+" ở phía trên
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
1. Một cửa sổ sẽ xuất hiện. Chọn giao diện mô hình lớn chung và đặt tên cho nó. Điều này sẽ sao chép các cài đặt và API của giao diện mô hình lớn chung hiện tại.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
1. Kích hoạt giao diện đã sao chép và cấu hình nó riêng biệt. Giao diện đã sao chép có thể chạy song song với giao diện gốc, cho phép bạn sử dụng nhiều cài đặt khác nhau đồng thời.
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

### Giải thích tham số

1. #### Địa chỉ API

    `Địa chỉ API` của hầu hết các nền tảng mô hình lớn phổ biến có thể được chọn trong danh sách thả xuống, nhưng có thể bị thiếu một số. Đối với các API không được liệt kê, vui lòng tự tham khảo tài liệu của nền tảng để điền.

1. #### API Key

    `API Key` có thể lấy được trên nền tảng. Đối với nhiều Key được thêm vào, hệ thống sẽ tự động luân phiên và điều chỉnh trọng số của Key dựa trên phản hồi lỗi.

1. #### Model

    Với hầu hết các nền tảng, sau khi điền `Địa chỉ API` và `API Key`, nhấp vào nút làm mới bên cạnh `model` để lấy danh sách model khả dụng.

    Nếu nền tảng không hỗ trợ API lấy model và model bạn cần không có trong danh sách mặc định, vui lòng tham khảo tài liệu chính thức của API để điền model thủ công.

1. #### Xuất luồng (Streaming output)

    Khi bật, nội dung đầu ra của model sẽ được hiển thị theo luồng tăng dần. Nếu tắt, tất cả nội dung sẽ được hiển thị một lần sau khi model hoàn thành.

1. #### Ẩn quá trình suy nghĩ

    Khi bật, nội dung được bao bọc bởi thẻ \<think\> sẽ không được hiển thị. Nếu bật ẩn quá trình suy nghĩ, tiến độ suy nghĩ hiện tại sẽ được hiển thị.

1. #### Số lượng ngữ cảnh đính kèm

    Sẽ đính kèm một số lịch sử văn bản gốc và API dịch cho mô hình lớn để tối ưu hóa bản dịch. Đặt thành 0 sẽ tắt tối ưu hóa này.

    - **Tối ưu tỷ lệ trúng cache** - Đối với các nền tảng như DeepSeek, nền tảng sẽ tính phí thấp hơn cho đầu vào trúng cache. Khi kích hoạt, hình thức đính kèm ngữ cảnh sẽ được tối ưu để tăng tỷ lệ trúng cache.

1. #### Tùy chỉnh system prompt / Tùy chỉnh user message / Prefill

    Một số cách khác nhau để kiểm soát nội dung đầu ra, có thể thiết lập theo sở thích hoặc sử dụng mặc định.

    Trong prompt hệ thống tùy chỉnh và tin nhắn người dùng, bạn có thể sử dụng các trường để tham chiếu thông tin:
    - `{sentence}`: Văn bản cần dịch
    - `{srclang}` và `{tgtlang}`: Ngôn ngữ nguồn và ngôn ngữ đích. Nếu chỉ sử dụng tiếng Anh trong prompt, chúng sẽ được thay thế bằng bản dịch tiếng Anh của tên ngôn ngữ. Ngược lại, chúng sẽ được thay thế bằng bản dịch tên ngôn ngữ trong ngôn ngữ UI hiện tại.
    - `{contextOriginal[N]}` và `{contextTranslation[N]}` và `{contextTranslation[N]}`: N câu lịch sử văn bản gốc, bản dịch và cả hai. N không liên quan đến "số lượng ngữ cảnh đi kèm" và cần được thay thế bằng một số nguyên khi nhập vào.
    - `{DictWithPrompt[XXXXX]}`: Trường này có thể tham chiếu các mục trong "Danh sách Dịch Thuật Ngữ Riêng". **Nếu không tìm thấy mục phù hợp, trường này sẽ bị xóa để tránh làm hỏng nội dung dịch**. Ở đây, `XXXXX` là một đoạn hướng dẫn LLM sử dụng các mục đã cho để tối ưu hóa bản dịch. Nó có thể được tùy chỉnh hoặc vô hiệu hóa tin nhắn tùy chỉnh của người dùng để sử dụng lời nhắc mặc định.

1. #### Temperature / max tokens / top p / frequency penalty

    Đối với một số nền tảng và mô hình, các tham số như `top p` và `frequency penalty` có thể không được chấp nhận bởi giao diện, hoặc tham số `max tokens` đã bị loại bỏ và thay bằng `max completion tokens`. Việc kích hoạt hoặc hủy kích hoạt công tắc có thể giải quyết những vấn đề này.

1. #### Reasoning effort

    Đối với nền tảng Gemini, tùy chọn sẽ tự động ánh xạ thành `thinkingBudget` của Gemini, quy tắc ánh xạ: 
    
    minimal->0 (tắt suy nghĩ, nhưng không áp dụng cho model Gemini-2.5-Pro), low->512, medium->-1 (kích hoạt suy nghĩ động), high->24576.

1. #### Các tham số khác

    Trên đây chỉ cung cấp một số tham số phổ biến. Nếu nền tảng bạn sử dụng cung cấp các tham số hữu ích khác chưa được liệt kê, có thể tự thêm cặp khóa-giá trị.

## Các nền tảng mô hình lớn phổ biến

### Nền tảng mô hình lớn ở Âu Mỹ  

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

### Nền tảng mô hình lớn ở Trung Quốc  

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

### Mô hình lớn ngoại tuyến

Bạn cũng có thể sử dụng các công cụ như [llama.cpp](https://github.com/ggerganov/llama.cpp), [ollama](https://github.com/ollama/ollama) để triển khai các mô hình, sau đó điền địa chỉ và mô hình.

Bạn cũng có thể sử dụng các nền tảng như Kaggle để triển khai mô hình lên đám mây, trong trường hợp này bạn có thể cần sử dụng SECRET_KEY; nếu không, bạn có thể bỏ qua tham số SECRET_KEY.
