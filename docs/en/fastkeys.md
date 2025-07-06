# Shortcut Keys

::: tip
 To use shortcut keys, you first need to activate `Use Shortcut Keys`, then activate the specific shortcut key you want to use, and set its key combination.
:::

## General

1. #### Manual Translation {#anchor-_1}
    Reads input once from the current text input source and performs translation.
    For example, if the current mode is OCR, it will perform OCR again.

1. #### Auto Translation {#anchor-_2}
    Pauses/resumes automatic text reading from the current text input source.
    For example, if the current mode is HOOK, it will pause reading game text; if the current mode is OCR, it will pause automatic image recognition; if the current mode is clipboard, it will pause automatic reading from the clipboard.

1. #### Open Settings {#anchor-_3}
    N/A

1. #### Show/Hide Original Text {#anchor-_5}
    Toggles whether to display the original text, taking effect immediately.

1. #### Show/Hide Translation {#anchor-_51}
    Toggles whether to use translation, which is the main switch for translation. Turning it off will stop any translation.
    If translation has already been performed, turning it off will hide the translation results, and turning it back on will redisplay the current translation results.
    If no translation has been performed and it is switched from hidden to displayed, it will trigger translation for the current sentence.

1. #### Show/Hide History Text {#anchor-_6}
    Open or close the history text window.  

1. #### Mouse Pass-through Window {#anchor-_8}
    Toggles the mouse pass-through window state.
    This feature must be used in conjunction with the mouse pass-through window tool button to function correctly.

1. #### Lock Toolbar {#anchor-_9}
    When the toolbar is not locked, it will automatically hide when the mouse moves out; activating this will keep the toolbar always visible.
    When the toolbar is not locked and `Mouse Pass-through Window` is activated, the toolbar will only be displayed when the mouse moves to the **Mouse Pass-through Window button and the area to its left and right**; otherwise, it will be displayed as soon as the mouse enters the translation window.
    If window effects (Aero/Arylic) are used and the toolbar is not locked, the toolbar will be in the z-axis area above the text area, not on the y-axis above the text area. This is because, due to Windows, when window effects are used, if the toolbar is only hidden rather than shrunk to reduce its window height, the hidden toolbar will still be rendered with the Acrylic/Aero background, causing a blank area where the toolbar is located.

1. #### Word selection translation {#anchor-38}
    Translate the text currently selected by the mouse

    Prioritize the use of UIAutomation for text extraction. If the focus control of the current window does not support UIAutomationTextPattern, resulting in a failure to extract text, then read from the clipboard.
1. #### Show/Hide Translation Window {#anchor-_16}
    N/A

1. #### Exit {#anchor-_17}
    N/A

## HOOK

>[!WARNING]
>Available only in HOOK mode

1. #### Select Game {#anchor-_11}
    Pops up the game process selection window to select the game process to HOOK.

1. #### Select Text {#anchor-_12}
    Pops up the game text selection window to select which HOOKed text to translate.
    However, the text selection window will automatically pop up after selecting the process, and is actually used to change the selected text or modify some settings.

## OCR

1. #### Select OCR Range {#anchor-_13}
    **Available only in OCR mode**
    
    In OCR mode, selects the OCR area, or changes the OCR area, or when `OCR Settings` -> `Other` -> `Multi-region Mode` is activated, adds a new OCR area.

1. #### Show/Hide Range Box {#anchor-_14}
    **Available only in OCR mode**
    
    When no OCR range is selected, using this shortcut key will display the OCR range and automatically set the OCR range to the last selected OCR.

1. #### Clear OCR range {#anchor-_14_1}
    **Only available in OCR mode**
    
    Clear all selected ranges

1. #### Perform OCR Once {#anchor-_26}
    Similar to `Read Clipboard`, regardless of the current default text input source, it will first select the OCR range, then perform OCR once, and then proceed with the translation process.
    Generally used for, in HOOK mode, temporarily using OCR to translate selection branches when encountering them, or in OCR mode, temporarily recognizing a new occasional position.

1. #### Perform OCR Again {#anchor-_26_1}
    After using `Perform OCR Once`, using this shortcut key will perform OCR again in the original position without reselecting the recognition area.

## Clipboard

1. #### Read Clipboard {#anchor-36}
    The actual meaning is that regardless of the current default text input source, it reads text once from the clipboard and passes it to the subsequent translation/TTS/... process.

1. #### Copy to Clipboard {#anchor-_4}
    Copies the currently extracted text to the clipboard once. If you want to automatically extract to the clipboard, enable `Core Settings` → `Clipboard` → `Output` → `Auto Output Text` and underneath it `Content` → `Original Text`.

1. #### Copy Translation to Clipboard {#anchor-_28}
    Copies the translation instead of the original text to the clipboard.

## TTS

1. #### Auto Read {#anchor-_32}
    Toggles whether to automatically read aloud.

1. #### Read {#anchor-_7}
    Performs text-to-speech on the current text.
    This reading will ignore `Skip` (if the current text target is matched as `Skip` in `Voice Assignment`, using the shortcut key to read will ignore the skip and force reading).

1. #### Read Interrupt {#anchor-_7_1}
    Interrupts the reading.

## Game

1. #### Bind Window (Click to Cancel) {#anchor-_15}
    After binding the game window, `Window Scaling`, `Window Screenshot`, `Game Mute`, `Follow Game Window` -> `Cancel Topmost When Game Loses Focus` and `Move Synchronously When Game Window Moves`, as well as recording game time, become available.
    This shortcut key is available regardless of HOOK/OCR/clipboard mode.
    In HOOK mode, it will automatically bind the game window according to the connected game, but you can also use this shortcut key to reselect another window.
    In OCR mode, after binding the window, it additionally allows the OCR area and range box to move synchronously when the game window moves.
    In OCR/clipboard mode, after binding the window, it can also be associated with the current game settings in HOOK mode, thus using the game's proprietary translation optimization dictionary, etc.

1. #### Window Screenshot {#anchor-_21}
    Can take a screenshot of the bound window (default takes two screenshots, GDI and Winrt, both of which may fail). The best part is that if Magpie is currently being used for scaling, it will also take a screenshot of the scaled window.

1. #### Game Mute {#anchor-_22}
    After binding the game window (not just in HOOK mode, but also in OCR or clipboard mode, as long as the game window is bound), you can mute the game with one click, saving the trouble of muting the game in the system volume mixer.

1. #### Magpie Scaling {#anchor-41}
    Allows one-click full-screen scaling of the game window using the built-in Magpie.

1. #### Magpie Windowed Scaling {#anchor-42}
    Allows one-click windowed scaling of the game window using the built-in Magpie.

## Dictionary Lookup

1. #### Retrieve and search for words {#anchor-37}
    Search for words in the text currently selected by the mouse

    Prioritize the use of UIAutomation for text extraction. If the focus control of the current window does not support UIAutomationTextPattern, resulting in a failure to extract text, then read from the clipboard.
1. #### Word Lookup in a New Window {#anchor-40}
    Look up the currently selected text by the mouse in a new search window to avoid overwriting the ongoing search.

    Prioritize the use of UIAutomation for text extraction. If the focus control of the current window does not support UIAutomationTextPattern, resulting in a failure to extract text, then read from the clipboard.
1. #### OCR word search {#anchor-39}
    Select the OCR range for one OCR and then search for words

1. #### Anki Recording {#anchor-_29}
    Shortcut key for the recording function in the Anki add interface in the dictionary lookup window.

1. #### Anki Recording Example Sentence {#anchor-_30}
    Shortcut key for the recording function in the Anki add interface in the dictionary lookup window, but this shortcut key sets the recorded audio to the example sentence field.

1. #### Anki Add {#anchor-_35}
    Adds the word to Anki.

1. #### Read Word {#anchor-_33}
    Reads the word in the current dictionary lookup window.

## Customize

You can add more arbitrary shortcut keys by implementing the `OnHotKeyClicked` function yourself, which will be called when the shortcut key is triggered.
