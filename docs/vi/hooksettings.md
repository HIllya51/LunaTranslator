# HOOK Settings

## General Settings

1. ####  Code Page

    ::: info
    This setting is meaningful only when the text extracted from the game is a **multi-byte string with an unspecified encoding within the HOOK engine**. When the HOOK engine has already specified a code page, or the text is a **wide character string** or **UTF32** string, this setting has no meaning.
    :::
    This setting generally does not need to be modified. It is only necessary when some old engines (e.g., Yuris) may have GBK/BIG5/UTF8 in their official Chinese versions. If you cannot find the correct text, please send an [issue](https://lunatranslator.org/Resource/game_support) directly to me; modifying this setting is usually futile.

1. ####  Refresh Delay

    If you face one of the following situations:

        1. Text is extracted one or two characters at a time;
        2. Text is extracted line by line, pushing out the previous line, and only the last line is displayed;
        3. Text is correct but extracted very slowly;

    Then you need to adjust this option.

    For **1 and 2**, because the game text is displayed too slowly, and the refresh delay is too low, each time one or two characters or a line of text is extracted, it immediately refreshes. In this case, you need to **increase the refresh delay** or increase the game's text display speed.

    For **3**, you can **appropriately reduce the refresh delay** while paying attention not to cause situations **1 and 2**.

1. ####  Maximum Buffer Length

    Sometimes, text will refresh repeatedly without stopping. If the refresh delay is high and cannot be reduced, it will continue to receive text until the buffer is filled or the text stops refreshing to meet the refresh delay (usually when the game loses focus, so it generally waits until the buffer is filled).

    To solve this problem, you can appropriately reduce the buffer length, but be careful not to make the buffer length too short to be less than the actual text length.

1. ####  Maximum Cached Text Length

    Received historical text is cached. When viewing the content of a text item in the text selection window, the historical cached text is queried. If there are too many text items or the text refreshes repeatedly, it will cause too much cached text, making it more sluggish to view text (sometimes even when not viewing). In fact, most of the cached text here is useless; useful historical text can be viewed in historical text window. You can arbitrarily lower this value (default is 1000000, but it can be lowered to 1000).

## Dedicated Game Settings

1. #### Additional Hooks
    1. #### Win32 Universal Hook
        After activation, Win32 universal function hooks will be injected into the game, including GDI functions, D3DX functions, and string functions.
        Injecting too many hooks can slow down the game, so these hooks are not injected by default.
        When the correct text cannot be extracted, you can try enabling these two options.
    1. #### Special Codes
        This special code will only be recorded when **a special code is inserted** and **the text of the special code is selected**. The next time the game starts, this special code will be automatically inserted. This setting records all previously recorded special codes, from which you can add or delete special codes.

1. #### Delayed Injection
    Sometimes, the position in the game that needs to be hooked is on a dll, which will only load after the game has run for a short while. We also need to wait until the dll loads before we can proceed with the injection.

1. #### Dedicated HOOK Settings
    The settings made in the settings interface -> HOOK settings are default settings. When no dedicated HOOK settings have been specified for the game, the default settings will be used.
    
    To set up dedicated HOOK settings for a game, you need to go to the **Game Management**, open the **Game Settings** interface, and switch to the HOOK sub-tab in the game settings selection card. After unchecking **Follow Default**, you can then set up dedicated HOOK settings for the game.

    ::: details
    ![img](https://image.lunatranslator.org/zh/gamesettings/1.jpg)

    ![img](https://image.lunatranslator.org/zh/gamesettings/2.png)
    :::