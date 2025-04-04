# ネットワークサービス

## Webページ

1. #### /page/mainui

    メインウィンドウに表示されるテキスト内容と同期します。

1. #### /page/transhist

    翻訳履歴に表示されるテキスト内容と同期します。

1. #### /page/searchword

    単語検索ページ。/page/mainuiで単語をクリックして検索すると、このページが表示されます。

1. #### /

    上記3つのページを統合したページです。このウィンドウの/page/mainuiサブセクションで単語をクリックして検索すると、新しい検索ウィンドウが開かず、現在のウィンドウの/page/searchwordサブセクションで検索結果が表示されます。

## APIサービス

### HTTPサービス

1. #### /api/searchword

    クエリパラメータ`word`が必要です。

    `event/text-stream`を返します。各イベントは、辞書名`name`とHTMLコンテンツ`result`を含むJSONオブジェクトです。

### WebSocketサービス

1.  #### /api/ws/text/origin

    抽出されたすべての原文テキストを継続的に出力します。

1.  #### /api/ws/text/trans

    すべての翻訳結果を継続的に出力します。