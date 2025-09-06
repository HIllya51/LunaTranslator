async function myAsyncFunction() {
  let _srclang = '{srclang}';
  if (_srclang == 'auto') {
    let detector;
    const detectorCapabilities = await LanguageDetector.availability();
    if (detectorCapabilities == 'downloadable') {
      detector = await LanguageDetector.create({
        monitor(m) {
          m.addEventListener('downloadprogress', (e) => {
            console.log(`Downloaded ${e.loaded * 100}%`);
          });
        },
      });
    }
    else if (detectorCapabilities == 'available') {
      detector = await LanguageDetector.create();
    }
    else {
      throw new Error("Not Support")
    }
    const results = await detector.detect(`{query}`);
    _srclang = results[0].detectedLanguage;
  }
  const translatorCapabilities = await Translator.availability({
    sourceLanguage: _srclang,
    targetLanguage: '{tgtlang}',
  });
  let translator;
  if (translatorCapabilities == 'downloadable') {
    translator = await Translator.create({
      sourceLanguage: _srclang,
      targetLanguage: '{tgtlang}',
      monitor(m) {
        m.addEventListener('downloadprogress', (e) => {
          console.log(`Downloaded ${e.loaded * 100}%`);
        });
      },
    });
  }
  else if (translatorCapabilities == 'available') {
    translator = await Translator.create({
      sourceLanguage: _srclang,
      targetLanguage: '{tgtlang}',
    });
  }
  else {
    throw new Error(`Not Support ${_srclang} -> {tgtlang}`)
  }
  return await translator.translate(`{query}`);
}
myAsyncFunction();