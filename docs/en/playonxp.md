## Playing Ancient Games on an XP Virtual Machine and Extracting Text for Translation

**1. Running the Game in a Different Locale Using ntleas in the VM**

If the game displays garbled characters, you can use [ntleas](https://github.com/zxyacb/ntlea)'s x86\ntleas.exe to run the game in a different locale. Open cmd, switch to the ntleas\x86 folder, and run `ntleas.exe "absolute path to game.exe"`.

![img](https://image.lunatranslator.org/zh/playonxp/ntleas.png)

**2. Extracting Text Using LunaHook Windows XP Special Edition in the VM**

Download `[LunaHook](https://github.com/HIllya51/LunaHook/releases)`'s `Release_Chinese_winxp.zip`, copy it into the VM, and run it. Select the game's process, choose the game text, and then in the settings, activate `Copy to Clipboard`.

![img](https://image.lunatranslator.org/zh/playonxp/image.png)

**3. Translating on the Host Machine**

Set up shared clipboard functionality for the VM to transmit clipboard content from the VM to the host machine.
![img](https://image.lunatranslator.org/zh/playonxp/copy.png)

Run LunaTranslator on the host machine and switch the text input source from `HOOK` to `Clipboard`.
![img](https://image.lunatranslator.org/zh/playonxp/host.png)

---

The final effect is as follows:
![img](https://image.lunatranslator.org/zh/playonxp/effect.png)