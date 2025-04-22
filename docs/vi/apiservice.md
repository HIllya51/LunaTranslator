# Dịch vụ Mạng

## Trang Web

1. #### /page/mainui

    Đồng bộ với nội dung văn bản hiển thị trong cửa sổ chính.

1. #### /page/transhist

    Đồng bộ với nội dung văn bản hiển thị trong lịch sử dịch.

1. #### /page/dictionary

    Trang tra cứu từ. Trang này được kích hoạt khi nhấp vào một từ để tra cứu trong `/page/mainui`.

1. #### /

    Một trang hợp nhất kết hợp ba trang được đề cập ở trên. Khi nhấp vào một từ để tra cứu trong phần `/page/mainui` của cửa sổ này, nó sẽ không mở một cửa sổ tra cứu mới mà thay vào đó hiển thị kết quả trong phần `/page/dictionary` của cửa sổ hiện tại.

1. #### /page/translate

    Giao diện dịch thuật.

1. #### /page/ocr

    Giao diện OCR.

## Dịch vụ API

### Dịch vụ HTTP

1. #### /api/translate

   Tham số truy vấn `text` phải được chỉ định.

   Nếu tham số `id` (ID trình dịch) được chỉ định, trình dịch đó sẽ được sử dụng để dịch. Nếu không, API dịch nhanh nhất hiện có sẽ được trả về.

   Trả về `application/json`, bao gồm ID trình dịch `id`, tên `name`, và kết quả dịch `result`.

1. #### /api/dictionary

    Tham số truy vấn `word` phải được chỉ định.

    Nếu tham số `id` (ID từ điển) được chỉ định, nó sẽ trả về kết quả truy vấn của từ điển đó dưới dạng đối tượng `application/json`, chứa ID từ điển `id`, tên từ điển `name`, và nội dung HTML `result`. Nếu truy vấn thất bại, một đối tượng rỗng sẽ được trả về.

    Nếu không, nó sẽ truy vấn tất cả các từ điển và trả về `event/text-stream`, trong đó mỗi sự kiện là một đối tượng JSON chứa ID từ điển `id`, tên từ điển `name`, và nội dung HTML `result`.

1. #### /api/mecab

   Tham số truy vấn `text` phải được chỉ định.

   Trả về kết quả phân tích của Mecab cho `text`.

1. #### /api/tts

   Tham số truy vấn `text` phải được chỉ định.

   Trả về dữ liệu âm thanh nhị phân.

1. #### /api/ocr

   Sử dụng phương thức POST để gửi yêu cầu JSON chứa trường `image` với dữ liệu hình ảnh được mã hóa base64.

1. #### /api/list/dictionary  

    Liệt kê tất cả các từ điển hiện có.

1. #### /api/list/translator  

    Liệt kê tất cả các công cụ dịch thuật hiện có.

### Dịch vụ WebSocket

1.  #### /api/ws/text/origin

    Liên tục xuất tất cả các văn bản gốc được trích xuất.

1.  #### /api/ws/text/trans

    Liên tục xuất tất cả các kết quả dịch thuật.