## Detailed Explanation of Tool Buttons

?> All buttons can be hidden or displayed in `Display Settings` -> `Tool Buttons`.<br>
All buttons can be freely adjusted in position. Buttons can be set to alignment groups `Left` `Center` `Right`, and adjustments to relative positions will be limited within the alignment group.<br>
Button colors can be customized in `Display Settings` -> `Interface Settings` -> `Toolbar` -> `Button Colors`.<br>
Some buttons have two icons to indicate two different states. Some buttons only have one icon, but they use different colors to represent different states.

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css"> 

<style>
    i{
        color:blue;
        width:20px;
    }
    .fa-icon {
  visibility: hidden;
}
.btnstatus2{
    color:deeppink;
}
</style>

1. #### <i class="fa fa-rotate-right"></i> <i class="fa fa-icon fa-rotate-right"></i> Manual Translation
    The actual meaning is to read the input once from the current text input source and perform translation.
    For example, if the current mode is OCR, it will perform OCR again.

1. #### <i class="fa fa-forward"></i> <i class="btnstatus2 fa fa-forward"></i> Auto Translation
    The actual meaning is to pause/continue automatically reading text from the current text input source.
    For example, if the current mode is HOOK, it will pause reading game text; if the current mode is OCR, it will pause automatic image recognition; if the current mode is clipboard mode, it will pause automatic reading of the clipboard.

1. #### <i class="fa fa-gear"></i> <i class="fa fa-icon fa-rotate-right"></i> Open Settings
    N/A
1. #### <i class="fa fa-file"></i> <i class="fa fa-icon fa-rotate-right"></i> Read Clipboard
    The actual meaning is to read text once from the clipboard regardless of the current default text input source and pass it on to the subsequent translation/tts/... process

1. #### <i class="fa fa-heart"></i> <i class="fa fa-icon fa-rotate-right"></i> Favorites
    Able to create a small favorites folder for each game. It includes automatically query metadata for game-related pages such as vndb/bangumi/dlsite/, and you can also manually add some web pages associated with the game (such as game strategy pages) for easy viewing. It saves the trouble of creating and managing bookmarks in a browser.<br>
    Right clicking the button will bring up a menu listing the favorite web pages, while left clicking the button will bring up a window allowing editing of the favorite content.

1. #### <i class="fa fa-futbol"></i> <i class="fa fa-icon fa-rotate-right"></i> Game Settings
    When using HOOK mode to connect to a game, or using OCR mode to bind a game window, you can directly open the current game's settings window through this button
1. #### <i class="fa fa-mouse-pointer"></i> <i class="btnstatus2 fa fa-mouse-pointer"></i> Mouse Through Window
    After activating this button, the translation window will not respond to mouse clicks, but will pass the click event to the underlying window.<br>
    When placing the translation window above the game window's text box and activating this button, you can directly click the game's text box instead of the translation window.<br>
    When the mouse moves to the **area of the Mouse Through Window button and one button to the left and right**, it will automatically exit through to use the tool buttons; it will automatically restore through when moving out of the area.

1. #### <i class="fa fa-lightbulb"></i> <i class="btnstatus2 fa fa-lightbulb"></i> Background Window Transparency
    The function of this button is to switch the opacity of the translation window to 0 with one click. This switch will not cause the original opacity settings to be forgotten.
    
1. #### <i class="fa fa-lock"></i> <i class="btnstatus2 fa fa-unlock"></i> Lock Toolbar
    When the toolbar is not locked, it will automatically hide when the mouse moves out; after activation, the toolbar will always be displayed.<br>
    When the toolbar is not locked, if `Mouse Through Window` is activated, the toolbar will only be displayed when the mouse moves to the **area of the Mouse Through Window button and one button to the left and right**; otherwise, as long as the mouse enters the translation window, the toolbar will be displayed.<br>
    If the window effect (Aero/Arylic) is currently used and the toolbar is not locked, the toolbar will be in the area above the text area on the z-axis, not on the y-axis above the text area. This is because due to Windows, when using the window effect, if the toolbar is only hidden instead of reducing its window height, the hidden toolbar will still be rendered with the acrylic/Aero background, resulting in a blank area where the toolbar is located.
1. #### <i class="fa fa-link"></i> <i class="fa fa-icon fa-rotate-right"></i> Select Game
    **This button is only available in HOOK mode**<br>
    Clicking the button pops up the select game process window to select the game process to HOOK.
1. #### <i class="fa fa-tasks"></i> <i class="fa fa-icon fa-rotate-right"></i> Select Text
    **This button is only available in HOOK mode**<br>
    Clicking the button pops up the select game text window to select which text to translate that is HOOKed.<br>
    However, the select text window will automatically pop up after selecting the process, and this button is actually used to replace the selected text or modify some settings.
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> Select OCR Range
    **This button is only available in OCR mode**<br>
    In OCR mode, select the OCR area, or change the OCR area, or when activating `OCR Settings` -> `Other` -> `Multiple Area Mode`, add a new OCR area
1. #### <i class="fa fa-square"></i> <i class="fa fa-icon fa-rotate-right"></i> Show/Hide Range Box 
    **This button is only available in OCR mode**<br>
    When no OCR range is selected, use this button to display the OCR range, which will automatically set the OCR range to the last selected OCR.
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> Perform OCR Once
    This button is similar to `Read Clipboard`, regardless of the current default text input source, it will first select the OCR range, then perform OCR once, and then proceed with the translation process.<br>
    This button is generally used in HOOK mode, when encountering choices, to temporarily use OCR for translation of choices. Or in OCR mode, to temporarily recognize a new position that occasionally appears.<br>
1. #### <i class="fa fa-spinner"></i> <i class="fa fa-icon fa-rotate-right"></i> Perform OCR Again
    After using `Perform OCR Once`, use this button to perform OCR again at the original location without having to re-select the recognition area.
    
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> Proper Noun Translation_Direct Replacement
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> Proper Noun Translation_Global
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> Proper Noun Translation
1. #### <i class="fa fa-won"></i> <i class="fa fa-icon fa-rotate-right"></i> Translation Result Correction_Global
1. #### <i class="fa fa-won"></i> <i class="fa fa-icon fa-rotate-right"></i> Translation Result Correction
    The above five buttons have similar effects and are used to quickly open the translation optimization settings window to add new specified terms.<br>
    For `Global`, it will definitely open the global dictionary settings. For non-`Global`, when there is a bound game (HOOK linked game/clipboard, OCR bound window), it will open the game's dedicated dictionary settings, otherwise it will open the global dictionary settings.
1. #### <i class="fa fa-minus"></i> <i class="fa fa-icon fa-rotate-right"></i> Minimize to Tray
    N/A
1. #### <i class="fa fa-times"></i> <i class="fa fa-icon fa-rotate-right"></i> Exit
    N/A
1. #### <i class="fa fa-hand-paper"></i> <i class="fa fa-icon fa-rotate-right"></i> Move
    Drag the translation window.<br>
    In fact, when there is no button on the button bar, there is additional blank area, you can drag it at will. This button is just for reserving a drag position.
1. #### <i class="fa fa-compress"></i> <i class="fa fa-expand"></i> Window Scaling
    You can scale the game window (HOOK linked game/clipboard, OCR bound window) with one click (default uses the built-in Magpie, or you can set it to use your own downloaded Magpie, etc.).<br>
1. #### <i class="fa fa-camera"></i> <i class="fa fa-icon fa-rotate-right"></i> Window Screenshot
    You can take a screenshot of the bound window (it will take two screenshots by default, GDI and Winrt, both of which have a certain probability of failure). The best part is that if you are currently using Magpie for scaling, it will also take a screenshot of the enlarged window.<br>
    When left clicked, the screenshot will be saved to a file, and when right clicked, the screenshot will be saved to the clipboard.

1. #### <i class="fa fa-volume-off"></i> <i class="btnstatus2 fa fa-volume-up"></i> Game Mute
    After binding the game window (not just in HOOK mode, OCR or clipboard mode can also, as long as the game window is bound), you can mute the game with one click, saving the trouble of muting the game in the system volume mixer.
1. #### <i class="fa fa-eye"></i> <i class="btnstatus2 fa fa-eye-slash"></i> Show/Hide Original Text
    Toggle whether to display the original text, which will take effect immediately.

1. #### <i class="fa fa-toggle-on"></i> <i class="btnstatus2 fa fa-toggle-off"></i> Show/Hide Translation
    Toggle whether to use translation, which is the master switch for translation. If turned off, no translation will be performed.<br>
    If a translation has already been performed, turning it off will hide the translation result, and it will re-display the current translation result when turned back on.<br>
    If no translation has been performed and it is switched from hidden to display, it will trigger the translation of the current sentence.

1. #### <i class="fa fa-music"></i> <i class="fa fa-icon fa-rotate-right"></i> Read Out Loud
    Left-clicking the button will perform text-to-speech on the current text.<br>Right-clicking the button will interrupt the reading.<br>  
    This reading will ignore `Skip` (if in `Voice Settings`, the current text target is matched as `Skip`, then using the button for reading will ignore the skip and force the reading).
1. #### <i class="fa fa-copy"></i> <i class="fa fa-icon fa-rotate-right"></i> Copy to Clipboard
    Copy the currently extracted text to the clipboard once. If you want to automatically extract to the clipboard, you should activate `Text Input` -> `Text Output` -> `Clipboard` -> `Auto Output`.
1. #### <i class="fa fa-rotate-left"></i> <i class="fa fa-icon fa-rotate-right"></i> Show/Hide History Translation
    Open or close the window for historical translations.
1. #### <i class="fa fa-gamepad"></i> <i class="fa fa-icon fa-rotate-right"></i> Game Management
    Open the game manager interface.
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> Edit
    Open the edit window to edit the currently extracted text.<br>
    In this window, you can modify the text and then perform translation; or you can translate any text you enter yourself.
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> Edit_Translation History
    Open the translation history edit window for the current game.
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> Simulate Key Press Ctrl
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> Simulate Key Press Enter
    As above, it is used to send a simulated key press to the game window. It has some effect when using streaming/tablet.
1. #### <i class="fa fa-list-ul"></i> <i class="fa fa-icon fa-rotate-right"></i> Memo
    Open the memo window for the game you are currently playing. Each game has a separate memo file.<br>
    It can be used to temporarily write some notes, or copy the strategy into it to read and delete as you play, which is very convenient. It saves the trouble of opening a web page/separately opening a txt file, very practical.
1. #### <i class="fab fa-windows"></i> <i class="btnstatus2 fab fa-windows"></i> Bind Window (Some software does not support) (Click to cancel)
    **This button is very important, many features depend on this button to be set first before they can be used**<br>
    After binding the game window, `Window Scaling` `Window Screenshot` `Game Mute`, `Follow Game Window` -> `Unpin when Game Loses Focus` and `Synchronize with Game Window Movement`, as well as recording game time, etc., are available.
    This button is available regardless of HOOK/OCR/Clipboard mode.<br>
    In HOOK mode, it will automatically bind the game window according to the connected game, but you can also use this button to re-select other windows.<br>
    In OCR mode, after binding the window, it also allows the OCR area and range box to move automatically in sync with the movement of the game window.
    In OCR/Clipboard model, after binding the window, you can also link to the current game's game settings like in HOOK mode, to use the current game's dedicated translation optimization dictionary, etc.

1. #### <i class="fa fa-neuter"></i> <i class="btnstatus2 fa fa-neuter"></i> Always on Top
    Cancel/Always on Top translation window
1. #### <i class="fa fa-i-cursor"></i> <i class="btnstatus2 fa fa-i-cursor"></i> Selectable
    Make the text in the translation window's text area selectable. When selectable is activated, you cannot drag in the text area but can only drag the toolbar (because dragging is for selecting text)
1. #### <i class="fa fa-search"></i> <i class="fa fa-icon fa-rotate-right"></i> Look Up
    Open the look-up window.