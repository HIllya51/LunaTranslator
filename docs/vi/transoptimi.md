# Chức Năng của Các Tối Ưu Hóa Dịch Thuật

1. ## Bản dịch của proprietary noun {#anchor-noundict}

    Phương pháp này thay thế trực tiếp văn bản gốc bằng văn bản đã dịch trước khi dịch. Nó hỗ trợ sử dụng `Regex` và `Escape` để thực hiện các thay thế phức tạp hơn.

    Khi tải siêu dữ liệu từ VNDB, trò chơi sẽ truy vấn thông tin tên nhân vật để thiết lập làm từ điển định sẵn. Đối với người dùng tiếng Anh, các tên tiếng Anh được trích xuất sẽ được điền vào làm bản dịch tương ứng với văn bản gốc. Trong trường hợp khác, bản dịch sẽ được điền cùng nội dung với bản gốc để tránh ảnh hưởng đến bản dịch khi người dùng không thực hiện thay đổi.

    ::: details Ví dụ
    ![img](https://image.lunatranslator.org/zh/transoptimi/1.png)
    :::

1. ## Bản dịch của proprietary noun {#anchor-noundict}

    Đối với `Giao diện chung mô hình lớn`, nếu prompt của nó chứa `DictWithPrompt`, thì mục từ sẽ được đưa vào prompt của mô hình. Cách sử dụng tham khảo [tài liệu này](/vi/guochandamoxing.html#anchor-prompt).

    Đối với các bản dịch truyền thống khác, hoặc nếu prompt của `Giao diện chung mô hình lớn` không chứa `DictWithPrompt`, thì sẽ tham khảo cách làm của VNR, thay thế văn bản gốc bằng trình giữ chỗ `ZX?Z` (PS: tôi cũng không biết nghĩa này là gì). Nguồn dịch thường sẽ không phá hỏng trình giữ chỗ sau khi dịch, và sau đó trình giữ chỗ sẽ được thay thế bằng bản dịch.

    Đối với các mục từ chuyên dụng cho trò chơi, khuyến nghị không nên thêm vào mục Xử lý văn bản -> Tối ưu hóa dịch thuật. Khuyến nghị thêm các mục từ chuyên dụng cho trò chơi trong phần cài đặt của phương pháp này trong `Tối ưu hóa dịch thuật` của `Cài đặt trò chơi`.

    Khi tải siêu dữ liệu từ VNDB, trò chơi sẽ truy vấn thông tin tên nhân vật để thiết lập làm từ điển cài sẵn. Đối với người dùng tiếng Anh, văn bản tiếng Anh được trích xuất sẽ được điền vào làm bản dịch tương ứng với văn bản gốc. Ngược lại, bản dịch sẽ để trống để tránh ảnh hưởng đến bản dịch khi người dùng không thực hiện thay đổi.

    ::: details Thiết Lập Các Mục Nhập Cụ Thể của Trò Chơi
      Nên sử dụng:
      ![img](https://image.lunatranslator.org/zh/transoptimi/2.png)
      Thay vì:
      ![img](https://image.lunatranslator.org/zh/transoptimi/3.png)
    :::

1. ## Sửa kết quả dịch {#anchor-transerrorfix}

    Phương pháp này cho phép sửa chữa nhất định đối với kết quả dịch sau khi dịch và có thể sử dụng toàn bộ biểu thức để thực hiện các sửa chữa phức tạp.

1. ## Tối ưu hóa tùy chỉnh {#anchor-myprocess}

    Viết một script Python để xử lý phức tạp hơn

1. ## Bỏ qua các câu chỉ chứa dấu câu {#anchor-skiponlypunctuations}

    Không áp dụng.

## Tối Ưu Hóa Dịch Thuật Cụ Thể cho Trò Chơi

Trong `Cài Đặt Trò Chơi` -> `Tối Ưu Hóa Dịch Thuật`, nếu `Theo Mặc Định` bị tắt, các cài đặt tối ưu hóa dịch thuật cụ thể cho trò chơi sẽ được sử dụng.

Nếu `Kế Thừa Mặc Định` được bật, từ điển tối ưu hóa dịch thuật cụ thể cho trò chơi cũng sẽ sử dụng từ điển toàn cầu mặc định.