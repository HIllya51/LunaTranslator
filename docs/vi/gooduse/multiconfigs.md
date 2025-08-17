# Tạo nhiều tệp cấu hình

Trước đây, nếu muốn mở phần mềm với nhiều cấu hình khác nhau cùng lúc, cách duy nhất là sao chép toàn bộ phần mềm, gây lãng phí dung lượng.

Gần đây, tính năng này đã được tối ưu. Giờ đây, phần mềm có thể đọc tệp cấu hình từ thư mục được chỉ định, cho phép bạn sử dụng các cấu hình khác nhau chỉ bằng cách chỉ định thư mục cấu hình khi chạy.

Cách thực hiện:

1. Tạo lối tắt cho chương trình chính.

    ![img](https://image.lunatranslator.org/zh/multiconfigs.png)

1. Chỉnh sửa Thuộc tính -> Mục tiêu của lối tắt bằng cách thêm ` --userconfig=XXXX` vào cuối, trong đó `XXXX` là tên thư mục bạn muốn sử dụng làm cấu hình mới. Sau đó, khởi chạy phần mềm bằng lối tắt này.

    Nếu `XXXX` là thư mục chưa tồn tại, phần mềm sẽ khởi động với cài đặt mặc định và tạo thư mục này.

    Nếu `XXXX` là thư mục đã tồn tại, phần mềm sẽ sử dụng các tệp cấu hình trong thư mục đó. Bạn có thể sao chép thư mục userconfig cũ và chỉ định `XXXX` là tên thư mục đã sao chép, từ đó tạo ra cấu hình mới từ cấu hình trước đó.

    ![img](https://image.lunatranslator.org/zh/multiconfigs2.png)

    ![img](https://image.lunatranslator.org/zh/multiconfigs3.png)
