# Network Service

## Web Pages

1. #### /page/mainui

    Synchronizes with the text content displayed in the main window.

1. #### /page/transhist

    Synchronizes with the text content displayed in the translation history.

1. #### /page/searchword

    Word lookup page. This page is triggered when clicking a word for lookup in `/page/mainui`.

1. #### /

    A consolidated page combining the three pages mentioned above. When clicking a word for lookup in the `/page/mainui` sub-section of this window, it will not open a new lookup window but will instead display the results in the `/page/searchword` sub-section of the current window.

## API Services

### HTTP Service

1. #### /api/searchword

    Requires the query parameter `word`.

    Returns `event/text-stream`, where each event is a JSON object containing the dictionary name `name` and HTML content `result`.

### WebSocket Service

1.  #### /api/ws/text/origin

    Continuously outputs all extracted original texts.

1.  #### /api/ws/text/trans

    Continuously outputs all translation results.