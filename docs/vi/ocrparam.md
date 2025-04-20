# Phương thức Thực thi Tự động OCR

Để phù hợp với các phương thức làm mới văn bản khác nhau của nhiều trò chơi, phần mềm cung cấp bốn phương thức riêng biệt để tự động chụp ảnh màn hình từ trò chơi với tần suất nhất định.


## Thực thi Định kỳ

::: tip
Nếu bạn thấy các thông số của các cài đặt khác khó hiểu, vui lòng sử dụng phương pháp này thay thế, vì đây là cách tiếp cận đơn giản nhất.
:::

Phương pháp này thực thi định kỳ dựa trên "Khoảng thời gian Thực thi" và sử dụng "Ngưỡng Tương đồng Văn bản" để tránh dịch cùng một văn bản nhiều lần.


## Phân tích Cập nhật Hình ảnh

Phương pháp này sử dụng các thông số như "Ngưỡng Ổn định Hình ảnh", "Ngưỡng Nhất quán Hình ảnh" và "Ngưỡng Tương đồng Văn bản".

1. #### Ngưỡng Ổn định Hình ảnh

    Khi văn bản trò chơi không xuất hiện ngay lập tức (tốc độ văn bản không phải nhanh nhất), hoặc khi trò chơi có nền động hoặc các yếu tố live2D, hình ảnh được chụp sẽ liên tục thay đổi.

    Mỗi lần chụp ảnh màn hình, nó được so sánh với ảnh chụp màn hình trước đó để tính toán độ tương đồng. Khi độ tương đồng vượt quá ngưỡng, hình ảnh được coi là ổn định, và bước tiếp theo được thực hiện.

    Nếu có thể xác nhận rằng trò chơi hoàn toàn tĩnh, giá trị này có thể được đặt thành 0. Ngược lại, nếu không phải vậy, giá trị này nên được tăng lên một cách thích hợp.

1. #### Ngưỡng Nhất quán Hình ảnh

    Thông số này là thông số quan trọng nhất.

    Sau khi hình ảnh ổn định, hình ảnh hiện tại được so sánh với hình ảnh tại lần thực thi OCR cuối cùng (không phải ảnh chụp màn hình cuối cùng). Khi độ tương đồng thấp hơn ngưỡng này, được coi là văn bản trò chơi đã thay đổi, và OCR được thực hiện.

    Nếu tần suất OCR quá cao, giá trị này có thể được tăng lên một cách thích hợp; ngược lại, nếu nó quá chậm, có thể giảm xuống một cách thích hợp.

1. #### Ngưỡng Tương đồng Văn bản

    Kết quả của OCR không ổn định, và nhiễu loạn nhỏ trong hình ảnh có thể gây ra thay đổi nhỏ trong văn bản, dẫn đến lặp lại dịch thuật.

    Sau mỗi lần gọi OCR, kết quả OCR hiện tại được so sánh với kết quả OCR trước đó (sử dụng khoảng cách chỉnh sửa). Chỉ khi khoảng cách chỉnh sửa lớn hơn ngưỡng thì văn bản mới được đưa ra.


## Phân tích Cập nhật Hình ảnh + Thực thi Định kỳ

Kết hợp hai phương pháp trên, OCR được thực hiện ít nhất một lần mỗi "Khoảng thời gian Thực thi". Nó cũng sử dụng "Ngưỡng Tương đồng Văn bản" để tránh dịch văn bản giống nhau. Ngoài ra, OCR được thực hiện trong các khoảng thời gian dựa trên "Phân tích Cập nhật Hình ảnh", đặt lại bộ đếm thời gian khoảng.


## Kích hoạt Chuột/Bàn phím + Chờ Ổn định

1. #### Sự kiện Kích hoạt

    Theo mặc định, các sự kiện chuột/bàn phím sau đây kích hoạt phương pháp này: nhấn nút chuột trái, nhấn Enter, thả Ctrl, thả Shift và thả Alt. Nếu cửa sổ trò chơi được ràng buộc, phương pháp này chỉ được kích hoạt khi cửa sổ trò chơi là cửa sổ nền trước.

    Sau khi kích hoạt phương pháp, cần thời gian chờ ngắn để trò chơi hiển thị văn bản mới, xem xét rằng văn bản có thể không xuất hiện ngay lập tức (nếu tốc độ văn bản không phải là nhanh nhất).

    Một khi phương pháp được kích hoạt và đạt được sự ổn định, dịch thuật luôn được thực hiện, mà không cần xem xét đến sự tương đồng của văn bản.

    Nếu tốc độ văn bản là nhanh nhất, cả hai thông số sau đây có thể được đặt thành 0. Nếu không, thời gian cần chờ được xác định bởi các thông số sau:

1. #### Độ trễ (giây)

    Chờ trong thời gian trễ cố định (có độ trễ vốn có 0.1 giây được tích hợp để đáp ứng xử lý logic nội bộ của các động cơ trò chơi).

1. #### Ngưỡng Ổn định Hình ảnh

    Giá trị này tương tự như thông số cùng tên đã đề cập trước đó. Tuy nhiên, điều này chỉ được sử dụng để xác định xem việc hiển thị văn bản đã hoàn thành hay chưa, và do đó nó không chia sẻ cấu hình với thông số cùng tên ở trên.

    Do thời gian hiển thị không thể đoán trước của tốc độ văn bản chậm hơn, độ trễ cố định được chỉ định có thể không đủ. Hành động được thực hiện khi độ tương đồng giữa hình ảnh và ảnh chụp màn hình trước đó cao hơn ngưỡng.
