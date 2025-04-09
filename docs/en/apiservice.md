# Network Service

## Web Pages

1. #### /page/mainui

    Synchronizes with the text content displayed in the main window.

1. #### /page/transhist

    Synchronizes with the text content displayed in the translation history.

1. #### /page/dictionary

    Word lookup page. This page is triggered when clicking a word for lookup in `/page/mainui`.

1. #### /

    A consolidated page combining the three pages mentioned above. When clicking a word for lookup in the `/page/mainui` sub-section of this window, it will not open a new lookup window but will instead display the results in the `/page/dictionary` sub-section of the current window.

1. #### /page/translate

    Translation interface

## API Services

### HTTP Service

1. #### /api/translate

   The query parameter `text` must be specified.

   If the parameter `id` (translator ID) is specified, that translator will be used for translation. Otherwise, the fastest available translation API will be returned.

   Returns `application/json`, including the translator ID `id`, name `name`, and translation result `result`.

1. #### /api/dictionary

    The query parameter `word` must be specified.

    If the parameter `id` (the ID of the dictionary) is specified, it will return the query result of that dictionary as an `application/json` object, containing the dictionary ID `id`, dictionary name `name`, and HTML content `result`. If the query fails, an empty object will be returned.

    Otherwise, it will query all dictionaries and return `event/text-stream`, where each event is a JSON object containing the dictionary ID `id`, dictionary name `name`, and HTML content `result`.

1. #### /api/mecab

   The query parameter `text` must be specified.

   Returns Mecab's parsing result for `text`.

1. #### /api/tts

   The query parameter `text` must be specified.

   Returns audio binary data.

1. #### /api/ocr

   Use POST method to send a JSON request containing an `image` field with base64 encoded image data.

1. #### /api/list/dictionary  

    List all currently available dictionaries  

1. #### /api/list/translator  

    List all currently available translation tools  

### WebSocket Service

1.  #### /api/ws/text/origin

    Continuously outputs all extracted original texts.

1.  #### /api/ws/text/trans

    Continuously outputs all translation results.