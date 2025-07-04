# Functions and Usage of Various Text Processing Methods

::: info
Generally, in HOOK mode, sometimes incorrect text is read, such as repeated text or other messy text. In such cases, text processing is needed to resolve the issue.
:::

::: tip
If there are very complex error forms, you can activate multiple processing methods and adjust their execution order to obtain a rich combination of processing methods.
:::

::: tip
Most processing methods do not take effect when embedding translations to reduce the possibility of game crashes. The methods that can be used include: `Filter Newline Characters`, `String Replacement`,  `Custom Python Processing`, `Filter Angle Brackets <>`, `Remove Curly Braces {}`
:::

1. #### Filter Non-Japanese Character Set Characters in Text {#anchor-_remove_non_shiftjis_char}

    Sometimes, garbled text is hooked. Since this problem usually occurs in Japanese games, this method is preset to filter out **characters that cannot be encoded using the shift-jis character set**, for example:

    `エマさんԟのイԠラストは全部大好き！` will be processed into `エマさんのイラストは全部大好き！`

1. #### Filter Control Characters {#anchor-_remove_control}

    This method will filter out ASCII control characters in the text, such as `` etc.

1. #### Filter English Punctuation {#anchor-_remove_symbo}

    This method will filter out ```!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~``` in the text.

1. #### Filter Characters Outside「」 {#anchor-_remove_not_in_ja_bracket}

    For example: `こなみ「ひとめぼれってやつだよね……」` will be processed into `「ひとめぼれってやつだよね……」`

1. #### Remove Curly Braces {} {#anchor-_1}

    Many game scripts use {} and some other characters to add furigana to kanji, for example: `{kanji/furigana}` and `{kanji:furigana}`, such as `「{恵麻/えま}さん、まだ{起き/おき}てる？」` or `「{恵麻:えま}さん、まだ{起き:おき}てる？」` will be processed into `「恵麻さん、まだ起きてる？」`. It will first attempt to remove the furigana according to these patterns, and then remove all curly braces and their contents.

1. #### Extract Specified Number of Lines {#anchor-lines_threshold_1}

    This method will extract the number of lines specified by **Number of Lines to Extract**.

    If **Extract from End** is activated, it will extract the specified number of lines from the end of the text.

1. #### Remove Duplicate Characters _AAAABBBBCCCC->ABC {#anchor-_2}

    This is the most commonly used filter.

    Due to the way games sometimes draw text (e.g., drawing text, then shadow, then outline), HOOK mode may extract the same characters multiple times. For example, `恵恵恵麻麻麻さささんんんははは再再再びびび液液液タタタブブブへへへ視視視線線線ををを落落落とととすすす。。。` will be processed into `恵麻さんは再び液タブへ視線を落とす。`. The default repetition count is `1`, which automatically analyzes the number of repeated characters, but there may be inaccuracies, so it is recommended to specify a definite repetition count.

1. #### Remove Duplicate Lines _ABCDABCDABCD->ABCD {#anchor-_3}

    This is also common, similar to the above, but generally does not refresh repeatedly, but quickly refreshes multiple times. The effect is `恵麻さんは再び液タブへ視線を落とす。恵麻さんは再び液タブへ視線を落とす。恵麻さんは再び液タブへ視線を落とす。` will become `恵麻さんは再び液タブへ視線を落とす。`. Similarly, the default repetition count is `1`, which automatically analyzes the number of repeated characters, but there may be inaccuracies, so it is recommended to specify a definite repetition count.

1. #### Remove Duplicate Lines _S1S1S1S2S2S2->S1S2 {#anchor-_3_2}

    This is relatively complex; sometimes, the refresh count of each sentence is not exactly the same, so the program must analyze how to deduplicate. For example, `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。なんてニヤニヤしていると、恵麻さんが振り返った。私は恵麻さんの目元を優しくハンカチで拭う。私は恵麻さんの目元を優しくハンカチで拭う。` where `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。` repeats 3 times, `なんてニヤニヤしていると、恵麻さんが振り返った。` does not repeat, and `私は恵麻さんの目元を優しくハンカチで拭う。` repeats 2 times, the final analysis will get `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。なんてニヤしていると、恵麻さんが振り返った。私は恵麻さんの目元を優しくハンカチで拭う。`, where due to the complexity, there may be a few analysis errors, which is unavoidable, but generally, it can get the correct result.

1. #### Filter Angle Brackets <> {#anchor-_4}

    This is actually filtering HTML tags, but the name is written this way to avoid confusion for beginners. For example, `<div>`, `</div>`, and `<div id="dsds">` will be filtered. This is mainly used in TyranoScript games where the HOOK extracts the text as innerHTML, usually containing many such tags.

1. #### Filter Newline Characters {#anchor-_6EX}

    Originally named **Filter Newline Characters Language Adaptive**, the old **Filter Newline Characters** has been deprecated.

    If the source language is not Japanese, when filtering newline characters, they will be replaced with spaces instead of being filtered out to avoid multiple words being connected together.

1. #### Filter Numbers {#anchor-_91}

    N/A

1. #### Filter English Letters {#anchor-_92}

    N/A

1. #### Remove Duplicate Lines _ABCDBCDCDD->ABCD {#anchor-_10}

    This is also common. The reason for this is that sometimes the function HOOKed to display text has the displayed text as a parameter, which is called every time a character is displayed, and each time the parameter string points to the next character, resulting in the fact that the first call has already obtained the complete text, and subsequent calls output the remaining substring until the length decreases to 0. For example, `恵麻さんは再び液タブへ視線を落とす。麻さんは再び液タブへ視線を落とす。さんは再び液タブへ視線を落とす。んは再び液タブへ視線を落とす。は再び液タブへ視線を落とす。再び液タブへ視線を落とす。び液タブへ視線を落とす。液タブへ視線を落とす。タブへ視線を落とす。ブへ視線を落とす。へ視線を落とす。視線を落とす。線を落とす。を落とす。落とす。とす。す。。` will be analyzed to determine that the real text should be `恵麻さんは再び液タブへ視線を落とす。`

1. #### Remove Duplicate Lines _AABABCABCD->ABCD {#anchor-_13EX}

    This is also common. The reason for this is that every time a character is drawn, the previous characters are redrawn when the next character is drawn. For example, `恵麻恵麻さ恵麻さん恵麻さんは恵麻さんは再恵麻さんは再び恵麻さんは再び液恵麻さんは再び液タ恵麻さんは再び液タブ恵麻さんは再び液タブへ恵麻さんは再び液タブへ視恵麻さんは再び液タブへ視線恵麻さんは再び液タブへ視線を恵麻さんは再び液タブへ視線を落恵麻さんは再び液タブへ視線を落と恵麻さんは再び液タブへ視線を落とす恵麻さんは再び液タブへ視線を落とす。` will be analyzed to determine that the real text should be `恵麻さんは再び液タブへ視線を落とす。`

    When there are multiple lines of text, each line is processed separately according to the above logic, which brings more complexity. Due to the complexity, this processing often fails to handle correctly. If encountered, it is recommended to write a custom Python script to solve it.

1. #### Custom Python Processing {#anchor-_11}

    Write a Python script for more complex processing. When the processing script does not exist, it will automatically generate a `mypost.py` file and the following template in the userconfig directory:

    ```python
    def POSTSOLVE(line):
        return line
    ```

1. #### String Replacement {#anchor-stringreplace}

    Not only replacement but also mainly used for filtering. For example, fixed garbled characters, repeatedly refreshed inverted triangle characters, etc., can be filtered by replacing them with blanks.

    Both the `Regex` and `Escape` options can be activated simultaneously, or only one of them, or neither.

    When neither is activated, ordinary string replacement will be used.

    When `Escape` is activated, the input content will be treated as an escaped string rather than a string literal. For example, `\n` can be used to represent a newline character, thus enabling filtering of characters that appear only before or after newline characters.

    When `Regex` is activated, regular expression replacement will be used.