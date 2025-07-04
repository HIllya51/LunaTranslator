---  
# https://vitepress.dev/reference/default-theme-home-page  
layout: home  

hero:  
  name: "LunaTranslator"  
  # text: "Trình dịch Galgame, hỗ trợ HOOK, OCR, Clipboard và nhiều hơn nữa"  
  # tagline: 💡 Dịch nhanh chóng, học tiếng Nhật dễ dàng!  
  # image:  
  #   src: /assets/bg.jpg  
  #   alt: LunaTranslator  
  actions:  
    - theme: brand  
      text: Tải xuống và bắt đầu  
      link: ./README  
    - theme: alt  
      text: Hướng dẫn cơ bản  
      link: ./basicuse  
    - theme: alt  
      text: Github  
      link: https://github.com/HIllya51/LunaTranslator  

features:  
  - title: HOOK  
    details: Chủ yếu sử dụng HOOK để trích xuất văn bản trò chơi, tương thích với hầu hết các visual novel phổ biến và ít phổ biến.  
    link: ./hooksettings
  - title: Dịch nhúng  
    details: Một số trò chơi cũng hỗ trợ nhúng trực tiếp bản dịch vào trò chơi để có trải nghiệm nhập vai.  
    link: ./embedtranslate
  - title: Trình giả lập HOOK  
    details: Hỗ trợ trình giả lập HOOK để trích xuất văn bản trực tiếp từ hầu hết các trò chơi trên NS/PSP/PSV/PS2.  
    link: ./emugames
  - title: OCR  
    details: Mô hình OCR tích hợp có độ chính xác cao, hỗ trợ nhiều công cụ OCR trực tuyến & ngoại tuyến khác để trích xuất văn bản linh hoạt.  
    link: ./useapis/ocrapi
  - title: API dịch phong phú  
    details: Hỗ trợ hầu hết các công cụ dịch, bao gồm dịch bằng mô hình ngôn ngữ lớn, dịch ngoại tuyến và nhiều hơn nữa.  
    link: ./useapis/tsapi
  - title: Tích hợp từ điển & Anki  
    details: Hỗ trợ Mecab, MDict, từ điển trực tuyến và AnkiConnect.  
    link: ./qa1
  - title: Chuyển văn bản thành giọng nói  
    details: Hỗ trợ nhiều công cụ chuyển văn bản thành giọng nói trực tuyến & ngoại tuyến.  
    link: ./ttsengines
  - title: Nhận dạng giọng nói
    details: Trên Windows 10 và Windows 11, bạn có thể sử dụng tính năng Nhận dạng giọng nói của Windows.
    link: ./sr
