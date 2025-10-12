---  
# https://vitepress.dev/reference/default-theme-home-page  
layout: home  

hero:  
  name: "LunaTranslator"  
  # text: "Galgame翻訳ツール、HOOK、OCR、クリップボードなどをサポート"  
  # tagline: 💡 素早い翻訳、簡単な日本語学習！  
  # image:  
  #   src: /assets/bg.jpg  
  #   alt: LunaTranslator  
  actions:  
    - theme: brand  
      text: ソフトウェアダウンロード & よくある質問
      link: ./README  
    - theme: alt  
      text: 基本の使い方  
      link: ./basicuse  
    - theme: alt
      text: 作者を支援する
      link: ./support
    - theme: alt  
      text: Github  
      link: https://github.com/HIllya51/LunaTranslator  

features:  
  - title: HOOK  
    details: 主にHOOKを使用してゲームテキストを抽出し、ほぼすべての一般的およびニッチなビジュアルノベルに対応しています。  
    link: ./hooksettings
  - title: 埋め込み翻訳  
    details: 一部のゲームでは、翻訳を直接ゲームに組み込むことができ、没入感のある体験を提供します。
    link: ./embedtranslate
  - title: HOOKエミュレータ  
    details: NS/PSP/PSV/PS2のほとんどのゲームでHOOKエミュレータをサポートし、直接ゲームテキストを読み取ります。
    link: ./emugames
  - title: OCR  
    details: 高精度のOCRモデルを内蔵し、多くの他のオンライン＆オフラインOCRエンジンをサポートし、柔軟にテキストを読み取ります。  
    link: ./useapis/ocrapi
  - title: 豊富な翻訳API  
    details: ほとんどすべての翻訳エンジンをサポートし、大規模言語モデル翻訳、オフライン翻訳などを含みます。
    link: ./guochandamoxing
  - title: 言語学習
    details: 日本語の分かち書きと仮名振りをサポート、AnkiConnectに対応、Yomitanプラグインをサポート
    link: ./qa1
  - title: 音声合成  
    details: 多数のオンライン＆オフライン音声合成エンジンをサポートします。  
    link: ./ttsengines
  - title: 音声認識
    details: Windows 10とWindows 11では、Windows音声認識を使用できます。
    link: ./sr
