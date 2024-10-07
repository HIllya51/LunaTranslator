## Detailed Explanation of Shortcut Keys

### To use shortcut keys, you first need to activate `Use Shortcut Keys`, then activate the specific shortcut key you want to use, and set its key combination.

<!-- tabs:start -->

### **General**

1. #### Manual Translation
    Reads input once from the current text input source and performs translation.
    For example, if the current mode is OCR, it will perform OCR again.

1. #### Auto Translation
    Pauses/resumes automatic text reading from the current text input source.
    For example, if the current mode is HOOK, it will pause reading game text; if the current mode is OCR, it will pause automatic image recognition; if the current mode is clipboard, it will pause automatic reading from the clipboard.

1. #### Open Settings
    N/A

1. #### Show/Hide Original Text
    Toggles whether to display the original text, taking effect immediately.

1. #### Show/Hide Translation
    Toggles whether to use translation, which is the main switch for translation. Turning it off will stop any translation.
    If translation has already been performed, turning it off will hide the translation results, and turning it back on will redisplay the current translation results.
    If no translation has been performed and it is switched from hidden to displayed, it will trigger translation for the current sentence.

1. #### Show/Hide Historical Translations
    Opens or closes the historical translations window.

1. #### Mouse Pass-through Window
    Toggles the mouse pass-through window state.
    This feature must be used in conjunction with the mouse pass-through window tool button to function correctly.

1. #### Lock Toolbar
    When the toolbar is not locked, it will automatically hide when the mouse moves out; activating this will keep the toolbar always visible.
    When the toolbar is not locked and `Mouse Pass-through Window` is activated, the toolbar will only be displayed when the mouse moves to the **Mouse Pass-through Window button and the area to its left and right**; otherwise, it will be displayed as soon as the mouse enters the translation window.
    If window effects (Aero/Arylic) are used and the toolbar is not locked, the toolbar will be in the z-axis area above the text area, not on the y-axis above the text area. This is because, due to Windows, when window effects are used, if the toolbar is only hidden rather than shrunk to reduce its window height, the hidden toolbar will still be rendered with the Acrylic/Aero background, causing a blank area where the toolbar is located.

1. #### Show/Hide Translation Window
    N/A

1. #### Exit
    N/A

### **HOOK**

**Available only in HOOK mode**

1. #### Select Game
    Pops up the game process selection window to select the game process to HOOK.

1. #### Select Text
    Pops up the game text selection window to select which HOOKed text to translate.
    However, the text selection window will automatically pop up after selecting the process, and is actually used to change the selected text or modify some settings.

### **OCR**

1. #### Select OCR Range
    **Available only in OCR mode**
    In OCR mode, selects the OCR area, or changes the OCR area, or when `OCR Settings` -> `Other` -> `Multi-region Mode` is activated, adds a new OCR area.

1. #### Show/Hide Range Box
    **Available only in OCR mode**
    When no OCR range is selected, using this shortcut key will display the OCR range and automatically set the OCR range to the last selected OCR.

1. #### Select OCR Range - Immediate
    **Available only in OCR mode**
    The difference from `Select OCR Range` is that it requires one less mouse click.

1. #### Perform OCR Once
    Similar to `Read Clipboard`, regardless of the current default text input source, it will first select the OCR range, then perform OCR once, and then proceed with the translation process.
    Generally used for, in HOOK mode, temporarily using OCR to translate selection branches when encountering them, or in OCR mode, temporarily recognizing a new occasional position.

1. #### Perform OCR Again
    After using `Perform OCR Once`, using this shortcut key will perform OCR again in the original position without reselecting the recognition area.

### **Clipboard**

1. #### Read Clipboard
    The actual meaning is that regardless of the current default text input source, it reads text once from the clipboard and passes it to the subsequent translation/TTS/... process.

1. #### Copy to Clipboard
    Copies the currently extracted text to the clipboard once. If you want to automatically extract to the clipboard, you should activate `Text Input` -> `Text Output` -> `Clipboard` -> `Auto Output`.

1. #### Copy Translation to Clipboard
    Copies the translation instead of the original text to the clipboard.

### **TTS**

1. #### Auto Read
    Toggles whether to automatically read aloud.

1. #### Read
    Performs text-to-speech on the current text.
    This reading will ignore `Skip` (if the current text target is matched as `Skip` in `Voice Assignment`, using the shortcut key to read will ignore the skip and force reading).

1. #### Read Interrupt
    Interrupts the reading.

### **Game**

1. #### Bind Window (Click to Cancel)
    After binding the game window, `Window Scaling`, `Window Screenshot`, `Game Mute`, `Follow Game Window` -> `Cancel Topmost When Game Loses Focus` and `Move Synchronously When Game Window Moves`, as well as recording game time, become available.
    This shortcut key is available regardless of HOOK/OCR/clipboard mode.
    In HOOK mode, it will automatically bind the game window according to the connected game, but you can also use this shortcut key to reselect another window.
    In OCR mode, after binding the window, it additionally allows the OCR area and range box to move synchronously when the game window moves.
    In OCR/clipboard mode, after binding the window, it can also be associated with the current game settings in HOOK mode, thus using the game's proprietary translation optimization dictionary, etc.

1. #### Window Scaling
    Can scale the game window (HOOK linked game/clipboard, OCR bound window) with one click (default uses the built-in Magpie, or can be set to use a downloaded Magpie, etc.).

1. #### Window Screenshot
    Can take a screenshot of the bound window (default takes two screenshots, GDI and Winrt, both of which may fail). The best part is that if Magpie is currently being used for scaling, it will also take a screenshot of the scaled window.
    See [Practical Functions](/zh/usefulsmalltools.md?id=窗口截图amp画廊amp录音，捕捉每个精彩瞬间) for details.

1. #### Game Mute
    After binding the game window (not just in HOOK mode, but also in OCR or clipboard mode, as long as the game window is bound), you can mute the game with one click, saving the trouble of muting the game in the system volume mixer.

1. #### Magpie In-game Overlay
    **Valid only when using the built-in Magpie to scale the window**
    Shows/hides the in-game overlay of the built-in Magpie.

1. #### Gallery Recording
    Shortcut key for a recording function in game management.

### **Dictionary Lookup**

1. #### Anki Recording
    Shortcut key for the recording function in the Anki add interface in the dictionary lookup window.

1. #### Anki Recording Example Sentence
    Shortcut key for the recording function in the Anki add interface in the dictionary lookup window, but this shortcut key sets the recorded audio to the example sentence field.

1. #### Anki Add
    Adds the word to Anki.

1. #### Read Word
    Reads the word in the current dictionary lookup window.

<!-- tabs:end -->