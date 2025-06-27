# Chuyển văn bản thành giọng nói với các giọng khác nhau cho từng nhân vật

Đầu tiên, nếu văn bản hiện tại không chứa tên hoặc thông tin nhận dạng khác, bạn có thể chọn thêm văn bản tên trong bộ chọn văn bản. Văn bản hiển thị sẽ được sắp xếp theo thứ tự lựa chọn.

Sau đó, vào `Cài đặt trò chơi` -> `Giọng nói` (hoặc `Cài đặt giọng nói` trong giao diện cài đặt, nhưng đây sẽ là cài đặt toàn cục, không khuyến nghị cho cài đặt toàn cục), tắt `Theo mặc định`, sau đó bật `Gán giọng nói`, và thêm một hàng trong cài đặt của nó. Đặt `Điều kiện` thành `Chứa`, điền tên nhân vật vào `Mục tiêu`, và sau đó chọn giọng nói trong `Gán cho`.

![img](https://image.lunatranslator.org/zh/tts/1.png) 

Tuy nhiên, vì văn bản tên được chọn thêm, nội dung hiển thị và dịch bao gồm cả tên, và giọng nói cũng sẽ đọc tên. Để giải quyết vấn đề này, bật `Chỉnh sửa giọng nói`, nơi bạn có thể sử dụng biểu thức chính quy để lọc tên và các ký hiệu của nó.  

## Giải thích chi tiết về gán giọng nói

Khi văn bản hiện tại đáp ứng điều kiện, hành động được chỉ định trong `Gán cho` sẽ được thực thi.

#### Điều kiện

1. Regex  
    Có sử dụng biểu thức chính quy để đánh giá hay không.
1. Điều kiện  
    **Bắt đầu/Kết thúc** Khi được đặt thành Bắt đầu/Kết thúc, điều kiện chỉ được đáp ứng khi mục tiêu nằm ở đầu hoặc cuối văn bản.  
    **Chứa** Điều kiện được đáp ứng miễn là mục tiêu xuất hiện trong văn bản. Đây là một đánh giá dễ dãi hơn.  
    Khi `Regex` được bật đồng thời, biểu thức chính quy sẽ tự động được xử lý để tương thích với tùy chọn này.
1. Mục tiêu  
    Văn bản được sử dụng để đánh giá, thường là **tên nhân vật**.  
    Khi `Regex` được bật, nội dung sẽ được sử dụng như một biểu thức chính quy để đánh giá chính xác hơn.

#### Gán cho

1. Bỏ qua  
    Khi điều kiện được đáp ứng, bỏ qua việc đọc văn bản hiện tại.

1. Mặc định  
    Sử dụng giọng nói mặc định cho nội dung đáp ứng điều kiện. Thông thường, khi sử dụng một đánh giá rất dễ dãi, dễ gây ra kết quả sai. Di chuyển đánh giá được đặt thành hành động này trước một đánh giá dễ dãi hơn có thể tránh được kết quả sai.
1. Chọn giọng nói  
    Sau khi chọn, một cửa sổ sẽ bật lên để chọn công cụ giọng nói và giọng nói. Khi điều kiện được đáp ứng, giọng nói này sẽ được sử dụng để đọc.
