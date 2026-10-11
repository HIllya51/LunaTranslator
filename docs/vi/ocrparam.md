# Cài Đặt Tính Năng OCR


## Hiển thị bản dịch tại chỗ

Khi bật, bản dịch sẽ hiển thị ngay trong khung chọn OCR, phủ lên văn bản gốc. Có thể bật/tắt bất kỳ lúc nào qua menu chuột phải của khung OCR.

- Mỗi vùng văn bản được nhận dạng sẽ hiển thị bản dịch tương ứng ngay tại vị trí cũ; cỡ chữ tự động phù hợp với kích thước vùng, văn bản nghiêng cũng được hiển thị theo cùng góc nghiêng.
- Nền của bản dịch chỉ phủ phần văn bản, không phủ toàn bộ khung chọn. Màu nền, màu chữ và căn chỉnh được điều chỉnh trong **Kiểu dáng** của menu chuột phải (trong cài đặt OCR cũng có một bản tương tự, hai bên đồng bộ theo thời gian thực).
- Lớp phủ không chặn chuột, trò chơi phía dưới vẫn thao tác bình thường; phần mềm cũng không nhận dạng lại bản dịch của chính mình.
- Ở chế độ đa vùng, mỗi khung chọn nhận dạng và hiển thị độc lập.


## Phương Pháp Thực Thi Tự Động {#anchor-auto}

Để phù hợp với các phương pháp làm mới văn bản khác nhau của các trò chơi, phần mềm cung cấp bốn phương pháp khác nhau để tự động chụp ảnh màn hình từ trò chơi theo một tần suất nhất định.

::: tabs

== Thực Thi Định Kỳ

> [!TIP]
> Nếu bạn thấy các tham số của các cài đặt khác khó hiểu, vui lòng sử dụng phương pháp này, vì đây là cách đơn giản nhất.

Phương pháp này thực thi định kỳ dựa trên “Khoảng Thời Gian Thực Thi”.

1. #### Khoảng Thời Gian Thực Thi

    Khoảng thời gian giữa các lần thực thi OCR.

1. #### Ngưỡng Tương Đồng Văn Bản

    Kết quả OCR không ổn định, và các nhiễu nhỏ trong hình ảnh có thể gây ra những thay đổi nhỏ trong văn bản, dẫn đến việc dịch lặp lại.

    Sau mỗi lần gọi OCR, kết quả OCR hiện tại được so sánh với kết quả OCR trước đó (sử dụng khoảng cách chỉnh sửa). Chỉ khi khoảng cách chỉnh sửa lớn hơn ngưỡng, văn bản mới được xuất ra.

== Phân Tích Cập Nhật Hình Ảnh

Phương pháp này thực thi khi hình ảnh không còn thay đổi thường xuyên.

1. #### Ngưỡng Ổn Định Hình Ảnh

    Khi văn bản trong trò chơi không xuất hiện ngay lập tức (tốc độ văn bản không phải nhanh nhất), hoặc khi trò chơi có nền động hoặc các yếu tố live2D, các hình ảnh được chụp sẽ liên tục thay đổi.

    Mỗi lần chụp ảnh màn hình, hình ảnh được so sánh với hình ảnh trước đó để tính toán độ tương đồng. Khi độ tương đồng vượt quá ngưỡng, hình ảnh được coi là ổn định và bước tiếp theo được thực hiện.

    Nếu có thể xác nhận rằng trò chơi hoàn toàn tĩnh, giá trị này có thể được đặt là 0. Ngược lại, nếu không, giá trị này nên được tăng lên một cách phù hợp.

1. #### Ngưỡng Nhất Quán Hình Ảnh

    Tham số này là quan trọng nhất.

    Sau khi hình ảnh ổn định, hình ảnh hiện tại được so sánh với hình ảnh tại lần thực thi OCR cuối cùng (không phải lần chụp ảnh màn hình cuối cùng). Khi độ tương đồng thấp hơn ngưỡng này, được coi là văn bản trong trò chơi đã thay đổi và OCR được thực hiện.

    Nếu tần suất OCR quá cao, giá trị này có thể được tăng lên một cách phù hợp; ngược lại, nếu quá chậm, giá trị này có thể được giảm xuống một cách phù hợp.

1. #### Ngưỡng Tương Đồng Văn Bản

    Kết quả OCR không ổn định, và các nhiễu nhỏ trong hình ảnh có thể gây ra những thay đổi nhỏ trong văn bản, dẫn đến việc dịch lặp lại.

    Sau mỗi lần gọi OCR, kết quả OCR hiện tại được so sánh với kết quả OCR trước đó (sử dụng khoảng cách chỉnh sửa). Chỉ khi khoảng cách chỉnh sửa lớn hơn ngưỡng, văn bản mới được xuất ra.

== Kích Hoạt Chuột/Bàn Phím + Chờ Ổn Định

Phương pháp này trước tiên chờ sự kiện do người dùng kích hoạt, sau đó chờ đến khi hình ảnh không còn thay đổi thường xuyên rồi mới thực thi.

1. #### Sự Kiện Kích Hoạt

    Theo mặc định, các sự kiện chuột/bàn phím sau sẽ kích hoạt phương pháp này: nhấn chuột trái, nhấn Enter, nhả Ctrl, nhả Shift và nhả Alt. Nếu cửa sổ trò chơi được liên kết, phương pháp này chỉ được kích hoạt khi cửa sổ trò chơi là cửa sổ nền trước.

    Sau khi kích hoạt phương pháp, cần một khoảng thời gian chờ ngắn để trò chơi hiển thị văn bản mới, vì văn bản có thể không xuất hiện ngay lập tức (nếu tốc độ văn bản không phải nhanh nhất).

    Khi phương pháp được kích hoạt và đạt được sự ổn định, luôn thực hiện dịch thuật mà không xem xét độ tương đồng của văn bản.

    Nếu tốc độ văn bản là nhanh nhất, cả hai tham số sau có thể được đặt là 0. Nếu không, thời gian cần chờ được xác định bởi các tham số sau:

1. #### Độ Trễ (giây)

    Chờ một khoảng thời gian trễ cố định (có một độ trễ nội tại 0,1 giây được tích hợp để phù hợp với xử lý logic nội bộ của các công cụ trò chơi).

1. #### Ngưỡng Ổn Định Hình Ảnh

    Giá trị này tương tự như tham số đã đề cập trước đó với cùng tên. Tuy nhiên, giá trị này chỉ được sử dụng để xác định xem việc hiển thị văn bản đã hoàn tất hay chưa, và do đó không chia sẻ cấu hình với tham số cùng tên ở trên.

    Do thời gian hiển thị không thể đoán trước của tốc độ văn bản chậm hơn, một khoảng thời gian trễ cố định có thể không đủ. Hành động được thực hiện khi độ tương đồng giữa hình ảnh và ảnh chụp màn hình trước đó cao hơn ngưỡng.

1. #### Ngưỡng Tương Đồng Văn Bản

    Kết quả OCR không ổn định, và các nhiễu nhỏ trong hình ảnh có thể gây ra những thay đổi nhỏ trong văn bản, dẫn đến việc dịch lặp lại.

    Sau mỗi lần gọi OCR, kết quả OCR hiện tại được so sánh với kết quả OCR trước đó (sử dụng khoảng cách chỉnh sửa). Chỉ khi khoảng cách chỉnh sửa lớn hơn ngưỡng, văn bản mới được xuất ra.

:::
