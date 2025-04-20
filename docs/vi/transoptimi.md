# Chức năng của Các Tối ưu hóa Dịch thuật Khác nhau

1. ## Dịch Danh từ Riêng - Thay thế Trực tiếp

    Phương pháp này thay thế trực tiếp văn bản gốc bằng văn bản đã dịch trước khi dịch. Nó hỗ trợ sử dụng `Regex` và `Escape` cho các thay thế phức tạp hơn.

    Khi trò chơi tải siêu dữ liệu từ VNDB, nó truy vấn tên nhân vật của trò chơi như một từ điển đặt trước. Tuy nhiên, bản dịch là bằng tiếng Anh do VNDB, và bạn có thể sửa đổi chúng thành tiếng Trung.

    ::: details Ví dụ
    ![img](https://image.lunatranslator.org/zh/transoptimi/1.png)
    :::

1. ## Dịch Danh từ Riêng

    Nếu sử dụng `mô hình lớn sakura` và đặt định dạng lời nhắc để hỗ trợ lời nhắc từ điển gpt, nó sẽ được chuyển đổi thành định dạng từ điển gpt. Nếu không, nó sẽ tham khảo cách tiếp cận VNR, thay thế văn bản gốc bằng giữ chỗ `ZX?Z` (ps: Tôi không biết điều này có nghĩa là gì), và sau khi dịch nguồn, giữ chỗ thường không bị phá hủy. Sau đó, sau khi dịch, giữ chỗ sẽ được thay thế bằng bản dịch.

    Đối với các mục cụ thể của trò chơi, không nên thêm chúng vào `Xử lý Văn bản` -> `Tối ưu hóa Dịch thuật`. Trước đây, giá trị md5 của trò chơi được sử dụng để phân biệt các mục cho nhiều trò chơi, nhưng việc triển khai này không tốt lắm và đã bị loại bỏ. Bây giờ, nên thêm các mục cụ thể của trò chơi trong cài đặt `Cài đặt Trò chơi` -> `Tối ưu hóa Dịch thuật` cho phương pháp này.

    Cột cuối cùng `Bình luận` chỉ được sử dụng cho `Mô hình Lớn Sakura`; các bản dịch khác sẽ bỏ qua cột này.

    ::: details Đặt Mục Cụ thể cho Trò chơi
      Nên sử dụng:
      ![img](https://image.lunatranslator.org/zh/transoptimi/2.png)
      Thay vì:
      ![img](https://image.lunatranslator.org/zh/transoptimi/3.png)
    :::

1. ## Hiệu chỉnh Kết quả Dịch

    Phương pháp này cho phép thực hiện một số hiệu chỉnh đối với kết quả dịch sau khi dịch và có thể sử dụng toàn bộ biểu thức cho các hiệu chỉnh phức tạp.

## Tối ưu hóa Dịch thuật Cụ thể cho Trò chơi

Trong `Cài đặt Trò chơi` -> `Tối ưu hóa Dịch thuật`, nếu `Theo Mặc định` bị vô hiệu hóa, cài đặt tối ưu hóa dịch thuật cụ thể cho trò chơi sẽ được sử dụng.

Nếu `Kế thừa Mặc định` được kích hoạt, từ điển tối ưu hóa dịch thuật cụ thể cho trò chơi cũng sẽ sử dụng từ điển toàn cục mặc định.