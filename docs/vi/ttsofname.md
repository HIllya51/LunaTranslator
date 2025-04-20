# Tổng hợp Giọng nói

## Chuyển Văn bản thành Giọng nói Sử dụng Giọng Khác nhau cho Các Nhân vật Khác nhau

Đầu tiên, nếu văn bản hiện tại không chứa tên hoặc thông tin nhận dạng khác, bạn có thể chọn thêm văn bản tên trong bộ chọn văn bản. Văn bản hiển thị sẽ được sắp xếp theo thứ tự lựa chọn.

Sau đó, trong `Cài đặt Trò chơi` -> `Giọng nói` (hoặc `Cài đặt Giọng nói` trong giao diện cài đặt, nhưng đây sẽ là cài đặt toàn cục, không khuyến nghị cho cài đặt toàn cục), hãy tắt `Theo Mặc định`, sau đó kích hoạt `Gán Giọng nói`, và thêm một hàng trong cài đặt của nó. Đặt `Điều kiện` thành `Chứa`, điền tên nhân vật vào `Mục tiêu`, và sau đó chọn giọng nói trong `Gán Cho`.

![img](https://image.lunatranslator.org/zh/tts/1.png) 

Tuy nhiên, do văn bản tên được chọn thêm, nội dung hiển thị và được dịch bao gồm cả tên, và giọng nói cũng sẽ đọc tên. Để giải quyết vấn đề này, kích hoạt `Hiệu chỉnh Giọng nói`, nơi bạn có thể sử dụng biểu thức chính quy để lọc tên và các ký hiệu của nó.
Nếu `Áp dụng cho Bản dịch` cũng được kích hoạt, hiệu chỉnh giọng nói này cũng sẽ xóa tên khỏi nội dung hiển thị và được dịch, làm cho nội dung hiển thị giống như khi mục tên không được chọn.

![img](https://image.lunatranslator.org/zh/tts/3.png)   

## Giải thích Chi tiết về Gán Giọng nói

Khi văn bản hiện tại đáp ứng điều kiện, hành động được chỉ định trong `Gán Cho` sẽ được thực hiện.

#### Điều kiện

1. Regex
    Có sử dụng biểu thức chính quy để đánh giá hay không.
1. Điều kiện
    **Bắt đầu/Kết thúc** Khi được đặt thành Bắt đầu/Kết thúc, điều kiện chỉ được đáp ứng khi mục tiêu ở đầu hoặc cuối văn bản.
    **Chứa** Điều kiện được đáp ứng miễn là mục tiêu xuất hiện trong văn bản. Đây là đánh giá khoan dung hơn.
    Khi `Regex` được kích hoạt đồng thời, biểu thức chính quy sẽ tự động được xử lý để tương thích với tùy chọn này.
1. Mục tiêu
    Văn bản được sử dụng để đánh giá, thường là **tên nhân vật**.
    Khi `Regex` được kích hoạt, nội dung sẽ được sử dụng như một biểu thức chính quy để đánh giá chính xác hơn.

#### Gán Cho

1. Bỏ qua
    Khi điều kiện được đáp ứng, bỏ qua việc đọc văn bản hiện tại.

1. Mặc định
    Sử dụng giọng nói mặc định cho nội dung đáp ứng điều kiện. Thông thường, khi sử dụng đánh giá rất khoan dung, dễ gây ra sai tích cực. Di chuyển bộ đánh giá sang hành động này trước đánh giá khoan dung hơn có thể tránh sai tích cực.
1. Chọn Giọng nói
    Sau khi lựa chọn, một cửa sổ sẽ bật lên để chọn công cụ giọng nói và giọng nói. Khi điều kiện được đáp ứng, giọng nói này sẽ được sử dụng để đọc.
