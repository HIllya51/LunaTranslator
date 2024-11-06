## Playing Ancient Games on an XP Virtual Machine and Extracting Text for Translation

**1. Extracting Text Using LunaHook Windows XP Special Edition in the VM**

Download `[LunaHook](https://github.com/HIllya51/LunaTranslator/releases/tag/LunaHook)`'s `Release_English_winxp.zip`, copy it into the VM, and run it. Select the game's process, choose the game text, and then in the settings, activate `Copy to Clipboard`.

![img](https://image.lunatranslator.org/zh/playonxp/image.png)

**2. Translating on the Host Machine**

Set up shared clipboard functionality for the VM to transmit clipboard content from the VM to the host machine.
![img](https://image.lunatranslator.org/zh/playonxp/copy.png)

Run LunaTranslator on the host machine and switch the text input source from `HOOK` to `Clipboard`.
![img](https://image.lunatranslator.org/zh/playonxp/host.png)

---

The final effect is as follows:
![img](https://image.lunatranslator.org/zh/playonxp/effect.png)