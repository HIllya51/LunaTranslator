# Functions of Various Translation Optimizations

1. ## Proper Noun Translation {#anchor-noundict}

    This method directly replaces the original text with the translated text before translation. It supports using `Regex` and `Escape` for more complex replacements.

    When loading metadata from VNDB, the game queries character name information to set as a preset dictionary. For English users, the extracted English names are populated as translations corresponding to the original text. Otherwise, the translation is filled with the same content as the original to avoid affecting translations when users make no modifications.

    ::: details Example
    ![img](https://image.lunatranslator.org/zh/transoptimi/1.png)
    :::

1. ## Proper Noun Translation {#anchor-noundict}

    For the `Universal LLM Interface`, if its prompt includes `DictWithPrompt`, the term will be added to the model's prompt. For usage, please refer to [this document](/ja/guochandamoxing.html#anchor-prompt).

    For other traditional translations, or if the prompt of the `Universal LLM Interface` does not contain `DictWithPrompt`, the method follows VNR's approach: the original text is replaced with a placeholder `ZX?Z` (PS: I'm not sure what this means either). The translation source typically does not disrupt the placeholder during translation, and after translation, the placeholder is replaced with the translated text.

    For game-specific terms, it is recommended not to add them under Text Processing -> Translation Optimization. Instead, please add game-specific terms in the settings for this method under `Translation Optimization` in `Game Settings`.

    When loading metadata from VNDB, the game queries character name information to set as a preset dictionary. For English users, the extracted English text is populated as the translation corresponding to the original text. Otherwise, the translation is left empty to avoid affecting translations when users make no modifications.

    ::: details Setting Game-specific Entries
      It is recommended to use:
      ![img](https://image.lunatranslator.org/zh/transoptimi/2.png)
      Instead of:
      ![img](https://image.lunatranslator.org/zh/transoptimi/3.png)
    :::

1. ## Translation Result Correction {#anchor-transerrorfix}

    This method allows for certain corrections to the translation result after translation and can use the entire expression for complex corrections.

1. ## Custom Optimization {#anchor-myprocess}

    Write a Python script to perform more complex processing

1. ## Skip sentences that contain only punctuation. {#anchor-skiponlypunctuations}

    N/A

## Game-specific Translation Optimization

In `Game Settings` -> `Translation Optimization`, if `Follow Default` is deactivated, game-specific translation optimization settings will be used.

If `Inherit Default` is activated, the game-specific translation optimization dictionary will also use the default global dictionary.