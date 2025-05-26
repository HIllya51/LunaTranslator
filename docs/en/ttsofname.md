# Using Different Voices for Different Characters

First, if the current text does not contain names or other identifying information, you can additionally select the name text in the text selector. The displayed text will be arranged in the order of selection.

Then, in `Game Settings` -> `Voice` (or `Voice Settings` in the settings interface, but this will be a global setting, not recommended for global settings), deactivate `Follow Default`, then activate `Voice Assignment`, and add a row in its settings. Set `Condition` to `Contains`, fill in the character name in `Target`, and then select the voice in `Assign To`.

![img](https://image.lunatranslator.org/zh/tts/1.png) 

However, since the name text is additionally selected, the displayed and translated content includes the name, and the voice will also read the name. To solve this problem, activate `Voice Correction`, where you can use regular expressions to filter out the name and its symbols.

![img](https://image.lunatranslator.org/zh/tts/3.png)   

## Detailed Explanation of Voice Assignment

When the current text meets the condition, the action specified in `Assign To` is executed.

#### Conditions

1. Regex
    Whether to use a regular expression for judgment.
1. Condition
    **Start/End** When set to Start/End, the condition is met only when the target is at the start or end of the text.
    **Contains** The condition is met as long as the target appears in the text. This is a more lenient judgment.
    When `Regex` is activated simultaneously, the regular expression is automatically processed to be compatible with this option.
1. Target
    The text used for judgment, usually a **character name**.
    When `Regex` is activated, the content will be used as a regular expression for more accurate judgment.

#### Assign To

1. Skip
    When the condition is met, skip reading the current text.

1. Default
    Use the default voice for content that meets the condition. Usually, when using a very lenient judgment, it is easy to cause false positives. Moving the judgment set to this action before a more lenient judgment can avoid false positives.
1. Select Voice
    After selection, a window will pop up to select the voice engine and voice. When the condition is met, this voice will be used for reading.
