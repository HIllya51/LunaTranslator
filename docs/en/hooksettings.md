## Detailed Explanation of HOOK Settings

### Parameter Meanings of HOOK Settings

**1. Code Page**

?> This setting is meaningful only when the text extracted from the game is a **multi-byte string with an unspecified encoding within the HOOK engine**. When the HOOK engine has already specified a code page, or the text is a **wide character string** or **UTF32** string, this setting has no meaning.

This setting generally does not need to be modified. It is only necessary when some old engines (e.g., Yuris) may have GBK/BIG5/UTF8 in their official Chinese versions. If you cannot find the correct text, please send an [issue](https://lunatranslator.org/Resource/game_support) directly to me; modifying this setting is usually futile.

**3. Filter Repeatedly Refreshing Sentences**

A simple text filter implemented internally by the HOOK engine. This filter can slightly improve performance in cases of crazy repeated text refreshing, but it is generally not recommended because the rules are too simplistic and may sometimes disrupt genuine repetition patterns.

**4. Refresh Delay**

?> Relatively speaking, this is the most practical option.

If you face one of the following situations:

    1. Text is extracted one or two characters at a time;
    2. Text is extracted line by line, pushing out the previous line, and only the last line is displayed;
    3. Text is correct but extracted very slowly;

Then you need to adjust this option.

For **1 and 2**, because the game text is displayed too slowly, and the refresh delay is too low, each time one or two characters or a line of text is extracted, it immediately refreshes. In this case, you need to **increase the refresh delay** or increase the game's text display speed.

For **3**, you can **appropriately reduce the refresh delay** while paying attention not to cause situations **1 and 2**.

**5. Maximum Buffer Length**

Sometimes, text will refresh repeatedly without stopping. If the refresh delay is high and cannot be reduced, it will continue to receive text until the buffer is filled or the text stops refreshing to meet the refresh delay (usually when the game loses focus, so it generally waits until the buffer is filled).

To solve this problem, you can appropriately reduce the buffer length, but be careful not to make the buffer length too short to be less than the actual text length.

**6. Maximum Cached Text Length**

Received historical text is cached. When viewing the content of a text item in the text selection window, the historical cached text is queried. If there are too many text items or the text refreshes repeatedly, it will cause too much cached text, making it more sluggish to view text (sometimes even when not viewing). In fact, most of the cached text here is useless; useful historical text can be viewed in historical translations. You can arbitrarily lower this value (default is 1000000, but it can be lowered to 1000).

**7. Filter Lines Containing Garbled Text**

The garbled text filtering in text processing only filters out garbled characters, while this filter, upon receiving text, will discard the entire line of text if any garbled characters are detected. When the game refreshes a large number of sentences containing garbled text, you can appropriately use this option to filter out invalid sentences and improve performance.

**8. Use YAPI Injection**

This option can sometimes slightly improve comfort, but it may have compatibility issues, so it is not recommended.

<details>
  <summary>Detailed Explanation</summary>
When injecting a DLL into a game, the process injecting the DLL and the process being injected usually need to have the same bitness.

To solve this problem, Luna generally uses shareddllproxy32 and shareddllproxy64 to inject DLLs into games of different bitness.

However, when this proxy process runs, it may be intercepted by antivirus software for a while, causing stuttering or failure to run and needing to run again. In this case, you can use YAPI to directly use the main process of Luna for DLL injection.

In YAPI, if the game process and the Luna process have the same bitness, it will inject normally; if the bitness is different, it will use a special shellcode to achieve injection. This is also one reason why LunaHost32.dll is more likely to be detected by antivirus software.

Using YAPI injection is relatively smoother. However, it may be incompatible on ARM tablets.

When Luna runs with low privileges and the game runs with administrator privileges, this option will be ineffective, and it will fall back to the original mode and request permissions for injection.
</details>

## Default Settings and Game-specific Settings

The settings made in the settings interface -> HOOK settings are default settings. When no specific HOOK settings are specified for a game, the default settings are used.

To set specific HOOK settings for a game, you need to open the **Game Management** interface, open the **Game Settings** interface, switch to the HOOK sub-tab in the game settings tab, and uncheck **Follow Default** to set specific HOOK settings for the game.

**1. Special Code**

When **Insert Special Code** and **Select Special Code Text**, this special code will be recorded, and it will be automatically inserted the next time it starts. This setting records all previously recorded special codes and allows adding or deleting special codes.

**2. Delayed Injection**

Sometimes, the position in the game that needs to be hooked, on the DLL, requires the game to run for a short while before the DLL is loaded. We also need to wait for the DLL to load before injecting.

![img](https://image.lunatranslator.org/zh/gamesettings/1.jpg)

![img](https://image.lunatranslator.org/zh/gamesettings/2.jpg)