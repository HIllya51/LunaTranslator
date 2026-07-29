---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "LunaTranslator"
  # text: "Galgame переводчик, поддерживающий HOOK, OCR, буфер обмена и другие функции"
  # tagline: 💡 Быстрый перевод, легкое изучение японского!
  # image:
  #   src: /assets/bg.jpg
  #   alt: LunaTranslator
  actions:
    - theme: brand
      text: Загрузка программного обеспечения & Часто задаваемые вопросы
      link: ./README
    - theme: alt
      text: Основное использование
      link: ./basicuse
    - theme: alt
      text: Поддержка автора
      link: ./README.html#anchor-support
    - theme: alt
      text: Github
      link: https://github.com/HIllya51/LunaTranslator

features:
  - title: HOOK
    details: Основной метод - извлечение текста игры через HOOK, совместим практически со всеми популярными и редкими визуальными новеллами
    link: ./hooksettings
  - title: Встроенный перевод
    details: Некоторые игры также поддерживают прямое встраивание перевода в игру для более глубокого погружения
    link: ./embedtranslate
  - title: HOOK эмулятор
    details: Для большинства игр на NS/PSP/PSV/PS2 поддерживается прямое считывание игрового текста через HOOK эмулятор
    link: ./emugames
  - title: OCR
    details: Встроена высокоточная OCR модель, а также поддержка многих других онлайн и оффлайн OCR движков для гибкого считывания любого текста
    link: ./useapis/ocrapi
  - title: Богатые интерфейсы перевода
    details: Поддержка практически всех движков перевода, включая LLM-перевод, оффлайн-перевод и другие
    link: ./guochandamoxing
  - title: Изучение языков
    details: Поддерживает японскую сегментацию слов и аннотацию каной, поддерживает AnkiConnect, поддерживает плагин Yomitan
    link: ./qa1
  - title: Синтез речи
    details: Поддержка множества онлайн и оффлайн движков синтеза речи
    link: ./ttsengines
  - title: Распознавание речи
    details: На Windows 10 и Windows 11 можно использовать встроенное распознавание речи Windows.
    link: ./sr

