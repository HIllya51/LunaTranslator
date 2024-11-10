## Невозможно запустить программу?

1. #### Не удается найти важные компоненты

  <img src="https://image.lunatranslator.org/zh/cantstart/2.jpg">

  Решение: Закройте антивирусную программу, если ее невозможно закрыть (например, Windows Defender), добавьте в список доверенных, затем повторно загрузите.

  Примечание: Для реализации HOOK для извлечения текста из игры необходимо внедрить Dll в игру, shareddllproxy32.exe/LunaHost32.dll и несколько других файлов реализуют это, поэтому они особенно легко распознаются как вирусы. Программа в настоящее время автоматически собирается с помощью [Github Actions](https://github.com/HIllya51/LunaTranslator/actions), поэтому если сервер Github не заражен, она не может содержать вирусы, и вы можете спокойно добавить их в список доверенных.

  <details>
    <summary>Для Windows Defender метод: "Защита от вирусов и угроз" -> "Исключения" -> "Добавить или удалить исключения" -> "Добавить исключение" -> "Папка", добавьте папку Luna</summary>
    <img src="https://image.lunatranslator.org/zh/cantstart/4.png">
    <img src="https://image.lunatranslator.org/zh/cantstart/3.png">
  </details>

1. #### Error/PermissionError

  Если программа помещена в специальные папки, такие как `Program Files`, у нее может не быть прав на чтение и запись. Пожалуйста, запустите с правами администратора.

  <img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>
