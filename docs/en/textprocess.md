## Functions and Usage of Various Text Processing Methods

> Generally, in HOOK mode, sometimes incorrect text is read, such as repeated text or other messy text. In such cases, text processing is needed to resolve the issue.

> If there are very complex error forms, you can activate multiple processing methods and adjust their execution order to obtain a rich combination of processing methods.

**1. Filter Non-Japanese Character Set Characters in Text**

Sometimes, garbled text is hooked. Since this problem usually occurs in Japanese games, this method is preset to filter out **characters that cannot be encoded using the shift-jis character set**, for example:

`エマさんԟのイԠラストは全部大好き！` will be processed into `エマさんのイラストは全部大好き！`

**2. Filter Control Characters**

This method will filter out ASCII control characters in the text, such as `` etc.

**3. Filter English Punctuation**

This method will filter out ```!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~``` in the text.

**4. Filter Other Garbled Text**

This requires setting the allowed character encoding or Unicode range in the settings. Characters not allowed will be filtered out.

**5. Filter Characters Outside「」**

For example: `こなみ「ひとめぼれってやつだよね……」` will be processed into `「ひとめぼれってやつだよね……」`

**6. Remove Curly Braces {}**

This is not exactly as it seems; it is mainly used to filter Japanese furigana. Many game scripts use {} and some other characters to add furigana to kanji. It supports two furigana formats: `{汉字/注音}` and `{汉字:注音}`, for example:

`「{恵麻/えま}さん、まだ{起き/おき}てる？」` or `「{恵麻:えま}さん、まだ{起き:おき}てる？」` will be processed into `「恵麻さん、まだ起きてる？」`

**7. Filter Text by Specified Word Count**

This method determines how to process based on the current text's word count.

If the text length is less than the minimum word count, the text will be filtered. For example, some games continuously refresh a single inverted triangle character in a static state, which can be filtered using this method.

If the text length exceeds the maximum word count, if **truncate instead of filter when exceeding** is activated, it will truncate the text to the specified word count; if not activated, the text will be completely filtered.

**8. Filter Text by Specified Line Count**

This is similar to the above but determines based on the text's line count. For example, it can be used to truncate the first 3 lines of text.

**9. Remove Duplicate Characters _AAAABBBBCCCC->ABC**

This is the most commonly used filter.

Due to the way games sometimes draw text (e.g., drawing text, then shadow, then outline), HOOK mode may extract the same characters multiple times. For example, `恵恵恵麻麻麻さささんんんははは再再再びびび液液液タタタブブブへへへ視視視線線線ををを落落落とととすすす。。。` will be processed into `恵麻さんは再び液タブへ視線を落とす。`. The default repetition count is `1`, which automatically analyzes the number of repeated characters, but there may be inaccuracies, so it is recommended to specify a definite repetition count.

**10. Filter Historical Duplicates LRU**

Sometimes, the way the game redraws text is not character by character but line by line, and it continuously redraws the current displayed text in a static state. For example, if the current display is two lines of text `你好` and `哈哈`, without using this method, it will repeatedly output `你好哈哈你好哈哈你好哈哈你好哈哈……`. Using this method, it caches several recently output texts, and when the cache is full and new text appears, it removes the earliest text in the cache, thus preventing recent texts from repeatedly refreshing.

**11. Remove Duplicate Lines _ABCDABCDABCD->ABCD**

This is also common, similar to the above, but generally does not refresh repeatedly, but quickly refreshes multiple times. The effect is `恵麻さんは再び液タブへ視線を落とす。恵麻さんは再び液タブへ視線を落とす。恵麻さんは再び液タブへ視線を落とす。` will become `恵麻さんは再び液タブへ視線を落とす。`. Similarly, the default repetition count is `1`, which automatically analyzes the number of repeated characters, but there may be inaccuracies, so it is recommended to specify a definite repetition count.

**12. Remove Duplicate Lines _S1S1S1S2S2S2->S1S2**

This is relatively complex; sometimes, the refresh count of each sentence is not exactly the same, so the program must analyze how to deduplicate. For example, `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。なんてニヤニヤしていると、恵麻さんが振り返った。私は恵麻さんの目元を優しくハンカチで拭う。私は恵麻さんの目元を優しくハンカチで拭う。` where `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。` repeats 3 times, `なんてニヤニヤしていると、恵麻さんが振り返った。` does not repeat, and `私は恵麻さんの目元を優しくハンカチで拭う。` repeats 2 times, the final analysis will get `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。なんてニヤしていると、恵麻さんが振り返った。私は恵麻さんの目元を優しくハンカチで拭う。`, where due to the complexity, there may be a few analysis errors, which is unavoidable, but generally, it can get the correct result.

**13. Filter Angle Brackets <>**

This is actually filtering HTML tags, but the name is written this way to avoid confusion for beginners. For example, `<div>`, `</div>`, and `<div id="dsds">` will be filtered. This is mainly used in TyranoScript games where the HOOK extracts the text as innerHTML, usually containing many such tags.

**14. Filter Newline Characters**

Originally named **Filter Newline Characters Language Adaptive**, the old **Filter Newline Characters** has been deprecated.

If the source language is not Japanese, when filtering newline characters, they will be replaced with spaces instead of being filtered out to avoid multiple words being connected together.

**15. Filter Numbers**

N/A

**16. Filter English Letters**

N/A

**17. Remove Duplicate Lines _ABCDBCDCDD->ABCD**

This is also common. The reason for this is that sometimes the function HOOKed to display text has the displayed text as a parameter, which is called every time a character is displayed, and each time the parameter string points to the next character, resulting in the fact that the first call has already obtained the complete text, and subsequent calls output the remaining substring until the length decreases to 0. For example, `恵麻さんは再び液タブへ視線を落とす。麻さんは再び液タブへ視線を落とす。さんは再び液タブへ視線を落とす。んは再び液タブへ視線を落とす。は再び液タブへ視線を落とす。再び液タブへ視線を落とす。び液タブへ視線を落とす。液タブへ視線を落とす。タブへ視線を落とす。ブへ視線を落とす。へ視線を落とす。視線を落とす。線を落とす。を落とす。落とす。とす。す。。` will be analyzed to determine that the real text should be `恵麻さんは再び液タブへ視線を落とす。`

**18. Remove Duplicate Lines _AABABCABCD->ABCD**

This is also common. The reason for this is that every time a character is drawn, the previous characters are redrawn when the next character is drawn. For example, `恵麻恵麻さ恵麻さん恵麻さんは恵麻さんは再恵麻さんは再び恵麻さんは再び液恵麻さんは再び液タ恵麻さんは再び液タブ恵麻さんは再び液タブへ恵麻さんは再び液タブへ視恵麻さんは再び液タブへ視線恵麻さんは再び液タブへ視線を恵麻さんは再び液タブへ視線を落恵麻さんは再び液タブへ視線を落と恵麻さんは再び液タブへ視線を落とす恵麻さんは再び液タブへ視線を落とす。` will be analyzed to determine that the real text should be `恵麻さんは再び液タブへ視線を落とす。`

**19. Remove Duplicate Lines _AABABCABCDEEFEFG->ABCDEFG**

This is similar to the above, but when there are multiple lines of text, each line is processed separately according to the above logic, which brings more complexity. Due to the complexity, this processing often fails to handle correctly. If encountered, it is recommended to write a custom Python script to solve it.

**20. Custom Python Processing**

Write a Python script for more complex processing. When the processing script does not exist, it will automatically generate a `mypost.py` file and the following template in the userconfig directory:

```
def POSTSOLVE(line):
    return line
```

**21. String Replacement**

Not only replacement but also mainly used for filtering. For example, fixed garbled characters, repeatedly refreshed inverted triangle characters, etc., can be filtered by replacing them with blanks.

Both the `Regex` and `Escape` options can be activated simultaneously, or only one of them, or neither.

When neither is activated, ordinary string replacement will be used.

When `Escape` is activated, the input content will be treated as an escaped string rather than a string literal. For example, `\n` can be used to represent a newline character, thus enabling filtering of characters that appear only before or after newline characters.

When `Regex` is activated, regular expression replacement will be used.