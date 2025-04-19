# OCR Automation Execution Methods

To accommodate the different text refresh methods of various games, the software offers four distinct methods to automatically capture screenshots from the game at a certain frequency.


## Periodic Execution

::: tip
If you find the parameters of the other settings difficult to understand, please use this method instead, as it is the simplest approach.
:::

This method executes periodically based on the “Execution Interval”.


## Analyze Image Update

This method utilizes parameters such as “Image Stability Threshold” and “Image Consistency Threshold”.

1. #### Image Stability Threshold

    When game text does not appear immediately (text speed is not the fastest), or when the game has a dynamic background or live2D elements, the captured images will continuously change.

    Each time a screenshot is taken, it is compared to the previous screenshot to calculate similarity. When the similarity exceeds the threshold, the image is considered stable, and the next step is performed.

    If it can be confirmed that the game is completely static, this value can be set to 0. Conversely, if it isn't, this value should be appropriately increased.

1. #### Image Consistency Threshold

    This parameter is the most important one.

    After the image stabilizes, the current image is compared to the image at the last OCR execution (not the last screenshot). When the similarity is lower than this threshold, it is considered that the game text has changed, and OCR is performed.

    If the OCR frequency is too high, this value can be appropriately increased; conversely, if it is too sluggish, it can be appropriately decreased.

## Mouse/Keyboard Trigger + Wait for Stability

1. #### Trigger Events

    By default, the following mouse/keyboard events trigger this method: pressing the left mouse button, pressing Enter, releasing Ctrl, releasing Shift, and releasing Alt. If the game window is bound, the method is triggered only when the game window is the foreground window.

    After triggering the method, a short wait period is required for the game to render new text, considering that text may not appear immediately (if the text speed is not the fastest).

    Once the method is triggered and stability is achieved, a translation is always performed, without considering the similarity of the text.

    If the text speed is the fastest, both of the following parameters can be set to 0. Otherwise, the time needed to wait is determined by the following parameters:

1. #### Delay (s)

    Wait for a fixed delay time (there is an inherent delay of 0.1 seconds built-in to accommodate the internal logic handling of game engines).

1. #### Image Stability Threshold

    This value is similar to the previously mentioned parameter with the same name. However, this is used solely to determine whether the text rendering is complete, and thus it does not share the configuration with the similarly named parameter above.

    Due to the unpredictable rendering times of slower text speeds, a specified fixed delay might not suffice. The action is executed when the similarity between the image and the previous screenshot is higher than the threshold.

## Text Similarity Threshold

The results of OCR are unstable, and minor disturbances in the image can cause slight changes in the text, leading to repeated translations.

After each OCR invocation, the current OCR result is compared to the previous OCR result (using edit distance). Only when the edit distance is greater than the threshold will the text be outputted.

