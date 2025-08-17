# Binding Game Window in OCR Mode

Typically, one very frustrating aspect of using other OCR software is often having to pay attention to the position of the game window and the translation window. It can be annoying if the translation window intersects with the screenshot area or if the game window needs to be switched to the background.

However, Luna's **Bind Window** setting perfectly resolves this annoyance.

Click the **Bind Window** button, then click on the game window. The button turns pink, indicating that the game window has been successfully bound.

![img](https://image.lunatranslator.org/zh/gooduseocr/bind.png)

![img](https://image.lunatranslator.org/zh/gooduseocr/bindok.png)

When this happens, there will be some significant changes:

1. **Screenshots will only capture the game window and not any other non-game windows.** This way, the translation window can be placed anywhere without causing dramatic changes due to intersecting with the screenshot area. Additionally, when the game window is obscured by another window, the screenshot will still only capture the game window.

2. **The OCR region will move in sync with the game window as the game window moves.** Thus, when you need to move the game window sometimes, there’s no need to move the OCR frame, especially if you have hidden the frame. There would be no need to show-move-hide it again.

In addition to these benefits, there are other advantages to binding the game window:

1. The game screenshot feature can more accurately capture the game window.

2. The gameplay time tracking function can more accurately record the time.

3. You can use the built-in Magpie or call your own downloaded Magpie via the tool button.

4. You can obtain the game's position and internal ID from the window handle, allowing for some personalized settings for the game, including dedicated language/TTS/translation optimization/text processing/Anki settings, etc.