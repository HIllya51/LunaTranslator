
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">

<style>
    i{
        color:blue;
        width:20px;
    }
    .fa-icon {
  visibility: hidden;
}
.btnstatus2{
    color:deeppink;
}
</style>

# Sử dụng OCR tạm thời trong chế độ HOOK  

Đôi khi chế độ HOOK không bắt được văn bản trong menu trò chơi, các lựa chọn, v.v. và việc chuyển sang chế độ OCR để nhận dạng rồi quay lại chế độ HOOK rất phiền phức.  

Thực tế đã có sẵn giải pháp tích hợp cho tình huống này: sử dụng nút "Thực hiện OCR một lần" <i class="fa fa-crop"></i> hoặc phím tắt.  

Nút này có biểu tượng mặc định giống với nút chọn vùng nhận dạng trong chế độ OCR và hiện đã được kích hoạt mặc định.  

Sau khi chọn vùng bằng nút này, nó chỉ thực hiện OCR một lần, sau đó thoát OCR và tiếp tục sử dụng HOOK để tự động trích xuất văn bản một cách liền mạch, khắc phục hoàn hảo một số thiếu sót của chế độ HOOK.  

**Do biểu tượng của nút này, nhiều người vốn muốn sử dụng OCR lại nhầm tưởng đây là nút OCR và sử dụng nó trong khi vẫn ở chế độ HOOK. Sau khi chọn vùng, bản dịch tự động không diễn ra. Trên thực tế, nút chế độ OCR chỉ xuất hiện sau khi chuyển sang chế độ OCR.**  

Đối với các lựa chọn ở vị trí cố định mà bạn không muốn chọn lại vùng mỗi lần, có thể sử dụng nút "Thực hiện OCR lại" <i class="fa fa-spinner"></i> hoặc phím tắt để thực hiện OCR bằng vùng đã chọn trước đó.  
