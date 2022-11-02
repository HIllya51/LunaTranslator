import win32api
import win32con
win32api.ShellExecute(None, "open", "C:\\dataH\\Locale.Emulator.2.5.0.1\\LEProc.exe ", "-run \"C:\\dataH\\パープルソフトウェア\\[211224] [パープルソフトウェア] クナド国記 + Original Soundtrack + ED Song + Visual Fan Book\\(18禁ゲーム) [211224] [パープルソフトウェア] クナド国記\\cmvs32.exe\"", "C:\\dataH\\パープルソフトウェア\\[211224] [パープルソフトウェア] クナド国記 + Original Soundtrack + ED Song + Visual Fan Book\\(18禁ゲーム) [211224] [パープルソフトウェア] クナド国記", win32con.SW_SHOW)
import os
print(os.path.dirname("C:\\dataH\\LunaTranslator\\LunaTranslator.exe") )