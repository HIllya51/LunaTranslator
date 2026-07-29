# Загрузка программного обеспечения & Часто задаваемые вопросы

## Скачать

| Операционная система | 64-bit |
| - | - |
| Windows 11 & 10(1803+) | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win10?doc=1"/> |

::: details Версия для совместимости со старыми ОС  

>[!WARNING]  
Эти версии обладают более низкой производительностью, работают менее стабильно, в них отсутствуют некоторые функции и возможности, а также они чаще подвергаются ложным срабатываниям антивирусного ПО. Не рекомендуется использовать, если нет особой необходимости.

| Операционная система | 32-bit | 64-bit |
| - | - | - |
| Windows 7 и выше | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_win7?doc=1"/> | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win7?doc=1"/> |
| Windows XP & Vista | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_winxp?doc=1"/> | |

:::

## Сообщество & Поддержка автора {#anchor-support}

Если у вас возникли трудности при использовании, вы можете присоединиться к нашему [Discord](https://discord.com/invite/ErtDwVeAbB).

<a href="https://discord.gg/invite/ErtDwVeAbB"><img src="https://img.shields.io/discord/1262692128031772733?style=for-the-badge&logo=discord&logoColor=white&label=Discord&color=5865F2" alt="Discord"></a>

Поддержка программного обеспечения требует усилий. Если вы считаете, что этот софт вам полезен, буду рад вашей поддержке через [Patreon](https://patreon.com/HIllya51). Ваша помощь станет стимулом для долгосрочного развития проекта. Спасибо!

<a href="https://patreon.com/HIllya51" target='_blank'><img width="200" src="/become_a_patron_4x1_black_logo_white_text_on_coral.svg"></a>

## Запуск & Обновление

После скачивания распакуйте в любую директорию

::: warning
Но не размещайте программу в **C:\Program Files** или других системных папках, иначе даже с правами администратора могут возникнуть проблемы с сохранением настроек и кэша, или программа может не запуститься.
:::

| LunaTranslator.exe | LunaTranslator_admin.exe | LunaTranslator_debug.bat |
| - | - | - |
| запуск в обычном режиме  | запуск с правами администратора. Требуется только для некоторых игр, где нужны права администратора для HOOK. В остальных случаях используйте обычный режим. | запуск с отображением консольного окна |


По умолчанию обновление происходит автоматически. Если автоматическое обновление не сработало, можно обновить вручную.

Для ручного обновления просто скачайте новую версию и распакуйте поверх старой.

Если хотите удалить и скачать заново, не удаляйте папку userconfig, иначе потеряете все настройки!!!

## Частые ошибки {#anchor-commonerros}

### Не найден важный компонент / Missing embedded Python3

::: danger
Иногда антивирус может удалять файлы, добавьте их в исключения и загрузите/распакуйте заново
:::

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

![img](https://image.lunatranslator.org/zh/missingpython.png) 

Решение: отключите антивирус, если отключение невозможно (например, Windows Defender) - добавьте в исключения, затем переустановите.

Примечание: Для извлечения игрового текста через HOOK необходимо внедрение DLL в игру. Эту функциональность реализуют файлы LunaSubprocess32.exe/LunaHost32.dll и некоторые другие, поэтому они часто ошибочно определяются как вирусы. Программа автоматически собирается через [Github Actions](https://github.com/HIllya51/LunaTranslator/actions). Если только серверы Github не заражены, вирусов быть не может, поэтому можно смело добавлять в исключения.

::: details Для Windows Defender: "Защита от вирусов и угроз" → "Исключения" → "Добавление или удаление исключений" → "Добавить исключение" → "Папка" → добавьте папку с программой Luna.
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### Ожидание инъекции DLL в игру... {#anchor-waitdll}

Решение - как указано выше.

### Error/FileNotFoundError

Если заранее не добавить исключения, антивирус может удалить некоторые необходимые компоненты после некоторого времени работы программы. Тогда при выборе процесса в режиме HOOK появится эта ошибка. Решение - как указано выше.

<img src="https://image.lunatranslator.org/zh/notfound.png" width=400>

### Error/PermissionError

Если программа размещена в системных папках типа `C:\Program Files`, она может работать некорректно.

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>
