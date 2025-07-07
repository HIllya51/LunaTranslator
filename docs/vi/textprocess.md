# Chức năng và Cách sử dụng các Phương pháp Xử lý Văn bản Khác nhau

::: info
Thông thường, trong chế độ HOOK, đôi khi văn bản được đọc không chính xác, chẳng hạn như văn bản bị lặp lại hoặc lộn xộn. Trong những trường hợp như vậy, cần xử lý văn bản để giải quyết vấn đề.
:::

::: tip
Nếu có các lỗi phức tạp, bạn có thể kích hoạt nhiều phương pháp xử lý và điều chỉnh thứ tự thực thi của chúng để tạo ra các tổ hợp phương pháp xử lý phong phú.
:::

::: tip
Hầu hết các phương pháp xử lý không có hiệu lực khi nhúng bản dịch để giảm khả năng trò chơi bị treo. Các phương pháp có thể sử dụng bao gồm: `Lọc ký tự xuống dòng`, `Thay thế chuỗi`, `Xử lý Python tùy chỉnh`, `Lọc dấu ngoặc nhọn <>`, `Xóa dấu ngoặc nhọn {}`
:::

1. #### Bộ lọc ký tự bộ ký tự không phải tiếng Nhật trong văn bản {#anchor-_remove_non_shiftjis_char}

    Đôi khi, văn bản bị lỗi ký tự. Vì vấn đề này thường xảy ra trong các trò chơi Nhật Bản, phương pháp này được thiết lập sẵn để lọc ra **các ký tự không thể mã hóa bằng bộ ký tự shift-jis**, ví dụ:

    `エマさんԟのイԠラストは全部大好き！` sẽ được xử lý thành `エマさんのイラストは全部大好き！`

1. #### Bộ lọc ký tự điều khiển {#anchor-_remove_control}

    Phương pháp này sẽ lọc ra các ký tự điều khiển ASCII trong văn bản, chẳng hạn như `` v.v.

1. #### Lọc chấm câu tiếng Anh {#anchor-_remove_symbo}

    Phương pháp này sẽ lọc ra ```!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~``` trong văn bản.

1. #### Lọc các ký tự khác ngoài "" {#anchor-_remove_not_in_ja_bracket}

    Ví dụ: `こなみ「ひとめぼれってやつだよね……」` sẽ được xử lý thành `「ひとめぼれってやつだよね……」`

1. #### Bỏ dấu ngoặc nhọn {} {#anchor-_1}

    Nhiều kịch bản trò chơi sử dụng {} và một số ký tự khác để thêm furigana vào kanji, ví dụ: `{kanji/furigana}` và `{kanji:furigana}`, chẳng hạn `「{恵麻/えま}さん、まだ{起き/おき}てる？」` hoặc `「{恵麻:えま}さん、まだ{起き:おき}てる？」` sẽ được xử lý thành `「恵麻さん、まだ起きてる？」`. Nó sẽ cố gắng xóa furigana theo các mẫu này trước, sau đó xóa tất cả dấu ngoặc nhọn và nội dung bên trong.

1. #### Chặn số dòng đã xác định {#anchor-lines_threshold_1}

    Phương pháp này sẽ trích xuất số dòng được chỉ định bởi **Số dòng cần trích xuất**.

    Nếu kích hoạt **Trích xuất từ cuối**, nó sẽ trích xuất số dòng được chỉ định từ cuối văn bản.

1. #### HOOK Loại bỏ các ký tự trùng lặp AAAABBBBCCCC->ABC {#anchor-_2}

    ::: info  
    Bộ lọc này chỉ có hiệu lực với văn bản đọc được ở chế độ HOOK  
    :::
    Đây là bộ lọc được sử dụng phổ biến nhất.

    Do cách trò chơi đôi khi vẽ văn bản (ví dụ: vẽ văn bản, sau đó là bóng, sau đó là viền), chế độ HOOK có thể trích xuất cùng một ký tự nhiều lần. Ví dụ, `恵恵恵麻麻麻さささんんんははは再再再びびび液液液タタタブブブへへへ視視視線線線ををを落落落とととすすす。。。` sẽ được xử lý thành `恵麻さんは再び液タブへ視線を落とす。`. Số lần lặp mặc định là `1`, tự động phân tích số ký tự lặp lại, nhưng có thể không chính xác, vì vậy nên chỉ định số lần lặp cụ thể.

1. #### HOOK Loại bỏ các dòng trùng lặp ABCDABCDABCD->ABCD {#anchor-_3}

    ::: info  
    Bộ lọc này chỉ có hiệu lực với văn bản đọc được ở chế độ HOOK  
    :::
    Điều này cũng phổ biến, tương tự như trên, nhưng thường không làm mới lặp lại mà làm mới nhanh nhiều lần. Kết quả là `恵麻さんは再び液タブへ視線を落とす。恵麻さんは再び液タブへ視線を落とす。恵麻さんは再び液タブへ視線を落とす。` sẽ trở thành `恵麻さんは再び液タブへ視線を落とす。`. Tương tự, số lần lặp mặc định là `1`, tự động phân tích số ký tự lặp lại, nhưng có thể không chính xác, vì vậy nên chỉ định số lần lặp cụ thể.

1. #### HOOK Loại bỏ các dòng trùng lặp S1S1S1S2S2S2->S1S2 {#anchor-_3_2}

    ::: info  
    Bộ lọc này chỉ có hiệu lực với văn bản đọc được ở chế độ HOOK  
    :::
    Điều này tương đối phức tạp; đôi khi, số lần làm mới của mỗi câu không hoàn toàn giống nhau, vì vậy chương trình phải phân tích cách loại bỏ trùng lặp. Ví dụ, `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。なんてニヤニヤしていると、恵麻さんが振り返った。私は恵麻さんの目元を優しくハンカチで拭う。私は恵麻さんの目元を優しくハンカチで拭う。` nơi `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。` lặp lại 3 lần, `なんてニヤニヤしていると、恵麻さんが振り返った。` không lặp lại, và `私は恵麻さんの目元を優しくハンカチで拭う。` lặp lại 2 lần, phân tích cuối cùng sẽ nhận được `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。なんてニヤしていると、恵麻さんが振り返った。私は恵麻さんの目元を優しくハンカチで拭う。`, nơi do sự phức tạp, có thể có một số lỗi phân tích, điều này không thể tránh khỏi, nhưng nhìn chung, nó có thể nhận được kết quả chính xác.

1. #### HOOK Loại bỏ các dòng trùng lặp ABCDBCDCDD->ABCD {#anchor-_10}

    ::: info  
    Bộ lọc này chỉ có hiệu lực với văn bản đọc được ở chế độ HOOK  
    :::

    Điều này cũng phổ biến. Lý do là đôi khi chức năng HOOK để hiển thị văn bản có văn bản hiển thị làm tham số, được gọi mỗi khi một ký tự được hiển thị, và mỗi lần chuỗi tham số trỏ đến ký tự tiếp theo, dẫn đến việc lần gọi đầu tiên đã nhận được văn bản đầy đủ, và các lần gọi sau đó xuất ra chuỗi con còn lại cho đến khi độ dài giảm xuống 0. Ví dụ, `恵麻さんは再び液タブへ視線を落とす。麻さんは再び液タブへ視線を落とす。さんは再び液タブへ視線を落とす。んは再び液タブへ視線を落とす。は再び液タブへ視線を落とす。再び液タブへ視線を落とす。び液タブへ視線を落とす。液タブへ視線を落とす。タブへ視線を落とす。ブへ視線を落とす。へ視線を落とす。視線を落とす。線を落とす。を落とす。落とす。とす。す。。` sẽ được phân tích để xác định rằng văn bản thực sự nên là `恵麻さんは再び液タブへ視線を落とす。`

1. #### HOOK Loại bỏ các dòng trùng lặp AABABCABCD->ABCD {#anchor-_13EX}

    ::: info  
    Bộ lọc này chỉ có hiệu lực với văn bản đọc được ở chế độ HOOK  
    :::
    Điều này cũng phổ biến. Lý do là mỗi khi một ký tự được vẽ, các ký tự trước đó được vẽ lại khi ký tự tiếp theo được vẽ. Ví dụ, `恵麻恵麻さ恵麻さん恵麻さんは恵麻さんは再恵麻さんは再び恵麻さんは再び液恵麻さんは再び液タ恵麻さんは再び液タブ恵麻さんは再び液タブへ恵麻さんは再び液タブへ視恵麻さんは再び液タブへ視線恵麻さんは再び液タブへ視線を恵麻さんは再び液タブへ視線を落恵麻さんは再び液タブへ視線を落と恵麻さんは再び液タブへ視線を落とす恵麻さんは再び液タブへ視線を落とす。` sẽ được phân tích để xác định rằng văn bản thực sự nên là `恵麻さんは再び液タブへ視線を落とす。`

    Khi có nhiều dòng văn bản, mỗi dòng được xử lý riêng theo logic trên, điều này mang lại nhiều phức tạp hơn. Do sự phức tạp, xử lý này thường không thể xử lý chính xác. Nếu gặp phải, nên viết một script Python tùy chỉnh để giải quyết.

1. #### Lọc ngoặc nhọn<> {#anchor-_4}

    Thực chất là lọc thẻ HTML, nhưng tên được viết như vậy để tránh nhầm lẫn cho người mới bắt đầu. Ví dụ, `<div>`, `</div>`, và `<div id="dsds">` sẽ được lọc. Điều này chủ yếu được sử dụng trong các trò chơi TyranoScript nơi HOOK trích xuất văn bản dưới dạng innerHTML, thường chứa nhiều thẻ như vậy.

1. #### Lọc ngắt dòng {#anchor-_6EX}

    Ban đầu được gọi là **Lọc Ký tự Xuống dòng Thích nghi Ngôn ngữ**, phiên bản cũ **Lọc Ký tự Xuống dòng** đã bị ngừng sử dụng.

    Nếu ngôn ngữ nguồn không phải là tiếng Nhật, khi lọc ký tự xuống dòng, chúng sẽ được thay thế bằng khoảng trắng thay vì bị lọc ra để tránh các từ bị nối liền nhau.

1. #### Lọc số {#anchor-_91}

    Không áp dụng.

1. #### Lọc thư tiếng Anh {#anchor-_92}

    Không áp dụng.

1. #### Xử lý Python tùy chỉnh {#anchor-_11}

    Viết một script Python để xử lý phức tạp hơn. Khi script xử lý không tồn tại, nó sẽ tự động tạo một tệp `mypost.py` và mẫu sau trong thư mục userconfig:

    ```python
    def POSTSOLVE(line):
        return line
    ```

1. #### Thay thế chuỗi {#anchor-stringreplace}

    Không chỉ thay thế mà còn chủ yếu được sử dụng để lọc. Ví dụ, các ký tự lỗi cố định, các ký tự tam giác ngược được làm mới lặp lại, v.v., có thể được lọc bằng cách thay thế chúng bằng khoảng trắng.

    Cả hai tùy chọn `Regex` và `Escape` có thể được kích hoạt đồng thời, hoặc chỉ một trong số chúng, hoặc không kích hoạt.

    Khi không kích hoạt, sẽ sử dụng thay thế chuỗi thông thường.

    Khi kích hoạt `Escape`, nội dung nhập vào sẽ được coi là chuỗi đã thoát thay vì chuỗi ký tự. Ví dụ, `\n` có thể được sử dụng để đại diện cho ký tự xuống dòng, do đó cho phép lọc các ký tự chỉ xuất hiện trước hoặc sau ký tự xuống dòng.

    Khi kích hoạt `Regex`, sẽ sử dụng thay thế biểu thức chính quy.