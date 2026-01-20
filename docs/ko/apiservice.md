# 네트워크 서비스

## 웹 페이지

1. #### /page/mainui

    주 창에 표시된 텍스트 내용과 동기화

1. #### /page/transhist

    히스토리 텍스트에 표시된 텍스트 내용과 동기화

1. #### /page/dictionary

    단어 조회 페이지. /page/mainui에서 단어를 클릭하여 조회할 때 이 페이지가 호출됩니다.

1. #### /

    위의 세 페이지를 통합한 하나의 페이지. 이 창의 /page/mainui 하위 영역에서 단어를 클릭하여 조회할 경우, 새로운 조회 창이 열리지 않고 현재 창의 /page/dictionary 하위 영역에서 조회가 진행됩니다.

1. #### /page/translate

    번역 인터페이스

1. #### /page/ocr

    OCR 인터페이스

1. #### /page/tts

    TTS 인터페이스

## API 서비스

### HTTP 서비스

1. #### /api/translate

    반드시 쿼리 파라미터 `text`를 지정해야 합니다.

    파라미터 `id`(번역기 ID)를 지정할 경우 해당 번역기를 사용하여 번역하며, 그렇지 않으면 가장 빠른 번역 인터페이스가 반환됩니다.

    `application/json`을 반환하며, 번역기 ID `id`, 이름 `name`, 번역 결과 `result`가 포함됩니다.

1. #### /api/dictionary

    반드시 쿼리 파라미터 `word`를 지정해야 합니다.

    파라미터 `id`(사전 ID)를 지정할 경우 해당 사전의 조회 결과인 `application/json` 객체를 반환하며, 사전 ID `id`, 사전 이름 `name`, HTML 내용 `result`가 포함됩니다. 조회 실패 시 빈 객체가 반환됩니다.

    그렇지 않으면 모든 사전을 조회하여 `event/text-stream`을 반환하며, 각 event는 JSON 객체로 사전 ID `id`, 사전 이름 `name`, HTML 내용 `result`를 포함합니다.

1. #### /api/mecab

    반드시 쿼리 파라미터 `text`를 지정해야 합니다.

    Mecab이 `text`를 분석한 결과를 반환합니다.

1. #### /api/tts

    반드시 쿼리 파라미터 `text`를 지정해야 합니다.

    오디오 바이너리를 반환합니다.

1. #### /api/ocr

    POST 메소드를 사용하여 json 요청을 전송하며, `image` 필드에 base64로 인코딩된 이미지가 포함되어야 합니다.

1. #### /api/list/dictionary

    현재 사용 가능한 사전 목록을 출력합니다.

1. #### /api/list/translator

    현재 사용 가능한 번역기 목록을 출력합니다.


1. #### /api/textinput

    매개변수 `text`를 반드시 지정해야 합니다  

### WebSocket 서비스

1.  #### /api/ws/text/origin

    추출된 모든 원본 텍스트를 지속적으로 출력합니다.

1.  #### /api/ws/text/trans

    모든 번역 결과를 지속적으로 출력할 예정입니다
