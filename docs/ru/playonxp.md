## Играть в старые игры на виртуальной машине с Windows XP и извлекать текст для перевода

**1. Использование ntleas для запуска игры в виртуальной машине**

Если у вас проблемы с повреждением текста в игре, вы можете использовать x86\ntleas.exe из [ntleas](https://github.com/zxyacb/ntlea) для запуска игры в нужной кодировке. Откройте cmd, перейдите в папку ntleas\x86 и запустите `ntleas.exe "Полный путь к исполняемому файлу игры.exe"`.

![img](https://image.lunatranslator.org/zh/playonxp/ntleas.png) 

**2. Использование LunaHook специальной версии для Windows XP в виртуальной машине для извлечения текста**

Скачайте `Release_Chinese_winxp.zip` из [LunaHook](https://github.com/HIllya51/LunaHook/releases), скопируйте его в виртуальную машину и запустите. Выберите процесс игры, выберите текст игры. Затем, в настройках, активируйте опцию `Копировать в буфер обмена`.

![img](https://image.lunatranslator.org/zh/playonxp/image.png) 

**3. Перевод на основном компьютере**

Настройте общий буфер обмена для виртуальной машины, чтобы передать содержимое буфера обмена из виртуальной машины на основной компьютер.
![img](https://image.lunatranslator.org/zh/playonxp/copy.png) 

На основном компьютере запустите LunaTranslator, переключите источник текстового ввода с `HOOK` на `Буфер обмена`.
![img](https://image.lunatranslator.org/zh/playonxp/host.png) 

---

Финальный результат будет выглядеть так:
![img](https://image.lunatranslator.org/zh/playonxp/effect.png)