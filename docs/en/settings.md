
# Settings

Access the settings window by clicking the settings button in the toolbar or the tray icon.


## Basic Settings

Choose your text output source. A pink ✓ indicates selection, while a gray × indicates inactive selection; only one can be selected at a time.

- When selecting OCR as the text input, you need to define the OCR region in the toolbar.

- Choosing Textractor (HOOK) as the text input will open a process selection window, followed by a text selection window after choosing a game.

- The default is clipboard mode, which automatically extracts and translates text from the clipboard.

![img](https://image.lunatranslator.org/zh/5.jpg)


## Translation Settings

Configure various translation engines. The developer (HIllya51) hasn't separated different types of translators into categories.

Supported translation engines include:

&emsp;&emsp;**Offline Translation**: Supports JBeijing7, Kingsoft FastAIT, and YiDianTong for offline translation.

&emsp;&emsp;Free Online Translation: Supports Baidu, Bing, Google, Ali, Youdao, Caiyun, Sogou, DeepL, Kingsoft, iFlytek, Tencent, ByteDance, Volcano, Papago, and Yeekit.

&emsp;&emsp;**Registered Online Translation**: Supports user-registered API keys for Baidu, Tencent, Youdao, Niutrans, Caiyun, Volcano, and DeepL.

&emsp;&emsp;**Pre-translation**: Supports loading human translations and aggregated machine pre-translations.

You can select any number of translation engines without restriction.

- The buttons represent: Enable/Disable translator / Set translation text color / Settings

- Offline translation, API online translation, and pre-translation require setup before use.

- For Google Translate and DeepL, you may need to set up a proxy to access them.

- Pre-translation supports fuzzy matching (particularly effective in OCR mode).

![img](https://image.lunatranslator.org/zh/6.jpg)


## HOOK设置

LocaleEmulator settings allow you to set the LocaleEmulator path (built-in for newer versions). Once set, you can launch games through LocaleEmulator.

- "Game Manager" stores previously hooked games for convenient launches (same as clicking "Open Game Manager" in the toolbar).

- "Record Translation File" saves extracted text to the "transkiroku" folder, outputting two files:

  1. **game_md5_game_executable_name.sqlite**: Records a single translation source output for generating "manual translation" files. Setting a preferred translation source prioritizes that source, and falls back to others if translation fails.

  2. **game_md5_game_executable_name.premt_synthesize.sqlite**: Used for "machine pre-translation" to record all valid translation results.

- "Export SQLite file to JSON" Exports to JSON for easy translation editing. Set the JSON file path as the "Manual Translation" file path to use manual translations.

- In clipboard and OCR modes, files are recorded with prefixes "0_copy" and "0_ocr" respectively.


[➔ See HOOK instructions for detailed usage](hooksetsumei.md)

![img](https://image.lunatranslator.org/zh/21.jpg)

 
## OCR Settings

In OCR mode, select your preferred OCR source.

- The local OCR is a built-in engine that's easy to use.

- Baidu OCR, OCRSpace, and Docsumo require API keys.

- Youdao OCR and Youdao Image Translation are experimental interfaces that may be unstable.

- Windows OCR requires Japanese language components installed on your system.

- Setting "Perform OCR at regular intervals" and specifying a maximum interval forces OCR to occur every X seconds, regardless if the game scene has changed or not.

[➔ See OCR instructions for detailed usage](ocrsetsumei.md)

![img](https://image.lunatranslator.org/zh/22.jpg)


## Display Settings

- Opacity sets the window background opacity.

- When "Show Original Text" is enabled, you can set options to display furigana and word segmentation results.

- Font styles include four options (Normal, Hollow, Outline, Shadow). The latter three advanced styles can be adjusted using "Hollow Line Width," "Outline Width," and "Shadow Strength" settings.

- "Original Text Color" sets the color for the source text, while "Background Color" sets the window background color.

- "Fill Color" is used for advanced font styles.

- "Selectable Mode" allows content selection within the translation window.


![img](https://image.lunatranslator.org/zh/7.jpg)

The four font styles are shown below:

![img](https://image.lunatranslator.org/zh/ziti1.jpg)
![img](https://image.lunatranslator.org/zh/ziti2.jpg)
![img](https://image.lunatranslator.org/zh/ziti3.jpg)
![img](https://image.lunatranslator.org/zh/ziti4.jpg)

Furigana (phonetic guide) display example:

![img](https://image.lunatranslator.org/zh/jiaming.jpg)

Tokenization (word segmentation) display example:

![img](https://image.lunatranslator.org/zh/fenci.jpg)


 
  
## Voice Settings

- Windows TTS requires Japanese language components installed on your system.

- Azure TTS and Volcano TTS are online services that may become unavailable in the future.

- VoiceRoid2 is an offline TTS engine.

- VOICEVOX is an open-source TTS engine, but it's relatively slow at Text-to-Speech.

![img](https://image.lunatranslator.org/zh/8.jpg)


 

## Translation Optimization

For text extracted via HOOK, you can set up simple processing operations to improve the content.

This includes common settings and some advanced options.

- "Simple Text Replacement" allows replacing or filtering extracted text.

- "Regular Expression Replacement" requires knowledge of Python's re.sub method (Regex).

- "Manual Translation for Proper Nouns" supports user-configured dictionaries for special terms (e.g., names, places).

- "Translation Result Correction" occurs after translation; forced replacement of translation results can be useful when noun translations fail with certain engines.

- This software partially supports using VNR shared dictionaries.

- Users familiar with Python can directly modify the LunaTranslator\LunaTranslator\postprocess\post.py file to implement custom processing.

![img](https://image.lunatranslator.org/zh/10.jpg)


## Dictionary Settings

With a dictionary configured, LunaTranslaotr can help you in your Japanese learning:

- MeCab setup + "Show Word Segmentation": Displays word boundaries (tokenization)
- MeCab + "Show Furigana": Applies furigana to kanji
- MeCab + "Show Different Colors for Parts of Speech": Highlights grammatical elements
- "Quick Word Lookup": Enables click-to-translate in the translation window

Note: Without MeCab, a basic built-in tokenizer will be used, providing limited furigana and segmentation without part-of-speech distinction.

![img](https://image.lunatranslator.org/zh/cishu.jpg)


![img](https://image.lunatranslator.org/zh/fenci.jpg)
![img](https://image.lunatranslator.org/zh/searchword.jpg)
![img](https://image.lunatranslator.org/zh/searchword2.jpg)

## Resource Download and Update

Automatic updates and links to commonly used resources.

![img](https://image.lunatranslator.org/zh/down.jpg)
 

## Hotkey Settings

Enable the use of hotkeys, where you can activate and configure specific hotkey settings as desired.

![img](https://image.lunatranslator.org/zh/quick.jpg)
