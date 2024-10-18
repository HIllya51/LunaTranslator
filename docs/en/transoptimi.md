## Functions of Various Translation Optimizations

#### **1. Proper Noun Translation - Direct Replacement**

This method directly replaces the original text with the translated text before translation. It supports using `Regex` and `Escape` for more complex replacements.

When the game loads metadata from VNDB, it queries the game's character names as a preset dictionary. However, the translations are in English due to VNDB, and you can modify them to Chinese.

<details>
  <summary>Example</summary>
  <img src="https://image.lunatranslator.org/zh/transoptimi/1.png">
</details>

#### **2. Proper Noun Translation**

If using the `sakura large model` and setting the prompt format to support the gpt dictionary prompt, it will be converted into the gpt dictionary format. Otherwise, it will refer to the VNR approach, replacing the original text with the placeholder `ZX?Z` (ps: I don't know what this means), and after the source translation, the placeholder is generally not destroyed. Then, after the translation, the placeholder will be replaced with the translation.

For game-specific entries, it is recommended not to add them in `Text Processing` -> `Translation Optimization`. In the past, the game's md5 value was used to distinguish entries for multiple games, but this implementation was not very good and has been deprecated. Now, it is recommended to add game-specific entries in the `Game Settings` -> `Translation Optimization` settings for this method.

The last column `Comment` is only used for the `Sakura Large Model`; other translations will ignore this column.

<details>
  <summary>Setting Game-specific Entries</summary>
  It is recommended to use:
  <img src="https://image.lunatranslator.org/zh/transoptimi/2.png">
  Instead of:
  <img src="https://image.lunatranslator.org/zh/transoptimi/3.png">
</details>

<details>
  <summary>Setting the Sakura Large Model Prompt Format to v0.10pre1 (Supports gpt Dictionary)</summary>
  <img src="https://image.lunatranslator.org/zh/transoptimi/4.png">
</details>

#### **3. Translation Result Correction**

This method allows for certain corrections to the translation result after translation and can use the entire expression for complex corrections.

## Game-specific Translation Optimization

In `Game Settings` -> `Translation Optimization`, if `Follow Default` is deactivated, game-specific translation optimization settings will be used.

If `Inherit Default` is activated, the game-specific translation optimization dictionary will also use the default global dictionary.