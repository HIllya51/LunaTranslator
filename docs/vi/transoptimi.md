# Chức Năng của Các Tối Ưu Hóa Dịch Thuật

1. ## Dịch Tên Riêng - Thay Thế Trực Tiếp

    Phương pháp này thay thế trực tiếp văn bản gốc bằng văn bản đã dịch trước khi dịch. Nó hỗ trợ sử dụng `Regex` và `Escape` để thực hiện các thay thế phức tạp hơn.

    Khi trò chơi tải siêu dữ liệu từ VNDB, nó truy vấn tên nhân vật của trò chơi như một từ điển cài sẵn. Tuy nhiên, các bản dịch là tiếng Anh do VNDB, và bạn có thể chỉnh sửa chúng thành tiếng Trung.

    ::: details Ví dụ
    ![img](https://image.lunatranslator.org/zh/transoptimi/1.png)
    :::

1. ## Dịch Tên Riêng

    Nếu sử dụng `mô hình lớn sakura` và thiết lập định dạng prompt để hỗ trợ prompt từ điển gpt, nó sẽ được chuyển đổi thành định dạng từ điển gpt. Nếu không, nó sẽ tham chiếu đến cách tiếp cận VNR, thay thế văn bản gốc bằng ký tự giữ chỗ `ZX?Z` (ps: Tôi không biết điều này có nghĩa là gì), và sau khi dịch nguồn, ký tự giữ chỗ thường không bị phá hủy. Sau đó, sau khi dịch, ký tự giữ chỗ sẽ được thay thế bằng bản dịch.

    Đối với các mục nhập cụ thể của trò chơi, không nên thêm chúng vào `Xử Lý Văn Bản` -> `Tối Ưu Hóa Dịch Thuật`. Trước đây, giá trị md5 của trò chơi được sử dụng để phân biệt các mục nhập cho nhiều trò chơi, nhưng cách triển khai này không tốt lắm và đã bị loại bỏ. Hiện tại, nên thêm các mục nhập cụ thể của trò chơi vào cài đặt `Cài Đặt Trò Chơi` -> `Tối Ưu Hóa Dịch Thuật` cho phương pháp này.

    Cột cuối cùng `Nhận Xét` chỉ được sử dụng cho `Mô Hình Lớn Sakura`; các bản dịch khác sẽ bỏ qua cột này.

    ::: details Thiết Lập Các Mục Nhập Cụ Thể của Trò Chơi
      Nên sử dụng:
      ![img](https://image.lunatranslator.org/zh/transoptimi/2.png)
      Thay vì:
      ![img](https://image.lunatranslator.org/zh/transoptimi/3.png)
    :::

1. ## Sửa Kết Quả Dịch

    Phương pháp này cho phép sửa chữa nhất định đối với kết quả dịch sau khi dịch và có thể sử dụng toàn bộ biểu thức để thực hiện các sửa chữa phức tạp.

## Tối Ưu Hóa Dịch Thuật Cụ Thể cho Trò Chơi

Trong `Cài Đặt Trò Chơi` -> `Tối Ưu Hóa Dịch Thuật`, nếu `Theo Mặc Định` bị tắt, các cài đặt tối ưu hóa dịch thuật cụ thể cho trò chơi sẽ được sử dụng.

Nếu `Kế Thừa Mặc Định` được bật, từ điển tối ưu hóa dịch thuật cụ thể cho trò chơi cũng sẽ sử dụng từ điển toàn cầu mặc định.