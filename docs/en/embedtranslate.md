## How to Use Embedded Translation?

> First, not all games support embedding. Second, embedding may cause the game to crash.

<details>
  <summary>If the 'Embed' line is not available in the text selection, it means embedding is not supported.</summary>
  <img src="https://image.lunatranslator.org/zh/embed/noembed.png"> 
  <img src="https://image.lunatranslator.org/zh/embed/someembed.png"> 
</details>

For games that support embedding, select the text entries that support embedding and activate it.

![img](https://image.lunatranslator.org/zh/embed/select.png) 

For entries that support embedding, you can freely choose whether to activate both **Display** and **Embed**. When both are activated, translations will be embedded in the game and more translations will be displayed in the software window; if only embedding is activated, only the embedded translations will be displayed in the game, and the software window will not display anything.

When starting embedded translation, garbled text often occurs. Game garbling is usually due to **character sets** and **fonts**. For English games, it is usually caused by the lack of Chinese **fonts**, for example:

![img](https://image.lunatranslator.org/zh/embed/luanma.png) 

At this time, you need to activate **Modify Game Font** in the **Embed Settings** and select an appropriate font to display Chinese characters.

![img](https://image.lunatranslator.org/zh/embed/ziti.png) 

After modifying the font, Chinese characters can be displayed correctly:

![img](https://image.lunatranslator.org/zh/embed/okembed.png) 

However, you may find that the embedded text is in Traditional Chinese, you can uncheck **Convert characters to Traditional/Japanese** in the **Embed Settings**.

> This is because **for many old Japanese galgames, they use their own built-in shift-jis character set processing and cannot correctly handle Chinese characters. By converting Chinese characters to similar Traditional/Japanese characters, the occurrence of garbled text can be reduced, so it is set to automatically convert Simplified Chinese to Traditional Chinese by default**. If garbled text appears after unchecking this setting, please restore it.

For newer game engines and most English games, Unicode character sets such as utf-8 or utf-16 are generally used (such as **KiriKiri**, **Renpy**, **TyranoScript**, **RPGMakerMV**, etc.), and even if garbled text appears, it is usually a font issue, not a character set issue.

![img](https://image.lunatranslator.org/zh/embed/fanti.png) 

After unchecking this setting, Simplified Chinese can be displayed correctly. However, for some games that cannot display Simplified Chinese correctly, you can try activating this option to see if it can be displayed normally.

![img](https://image.lunatranslator.org/zh/embed/good.png) 

** **

## Some Other Settings

**1. Keep Original Text** 

![img](https://image.lunatranslator.org/zh/embed/keeporigin.png) 

Due to the limitation of the number of text lines that the game can display, by default, there is no line break added between the translation and the original text. If you are sure it can accommodate, you can add a line break in front of the translation by adding a regex in **Translation Optimization** -> **Translation Result Correction**.

![img](https://image.lunatranslator.org/zh/embed/addspace.png) 

**2. Translation Waiting Time**

The principle of embedded translation is to pause the game in a certain function before the game displays the text, send the text to be displayed to the translator, wait for the translation, modify the text memory from the translated text, and then let the game continue to display the translation. Therefore, **when using a slower translation, it will definitely cause the game to stutter**. You can avoid long-term stuttering caused by slow translation by limiting the waiting time.

**3. Use Specified Translator**

When multiple translation sources are activated, you can choose to embed a specified translation with the best effect. If not activated, or if the specified translator is not activated, the fastest translation will be used to reduce game lag.


**4. Convert Characters to Traditional/Japanese**

Omitted

**5. Insert Spaces Between Overlapping Characters**

For some old Japanese game engines like SiglusEngine, they cannot correctly handle the width of Chinese characters and display them according to the width of English characters, causing overlapping of Chinese characters in embedded display. You can try adjusting this setting to solve this problem.

**6. Limit the Number of Characters per Line**

Sometimes some games have a limited number of characters per line, and content exceeding the length will be displayed outside the text box on the right and cannot be displayed. You can manually wrap the line to avoid this situation through this setting.

![img](https://image.lunatranslator.org/zh/embed/limitlength.png) 

**7. Modify Game Font**

Omitted

**8. Embedded Safety Check**

For games like Renpy, the extracted text often includes characters of syntax elements such as `{` `}` `[` `]`. If the translation source does not handle these contents correctly, it will break the syntax and cause the game to crash. Therefore, the software defaults to **skipping translation** of certain character combinations that may cause the game by regex matching. If you are not worried about game crashes, you can cancel this setting, or manually replace some finer-grained regex matches to reduce unnecessary skipping.

![img](https://image.lunatranslator.org/zh/embed/safeskip.png)