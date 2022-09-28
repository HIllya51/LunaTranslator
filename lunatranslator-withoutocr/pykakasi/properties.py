# -*- coding: utf-8 -*-
#  properties.py
#
# Copyright 2019 Hiroshi Miura <miurahr@linux.com>

import os

import pkg_resources


class Configurations:

    data_path = pkg_resources.resource_filename(__name__, "data")
    jisyo_hepburn_hira = "hepburnhira3.db"
    jisyo_passport_hira = "passporthira3.db"
    jisyo_kunrei_hira = "kunreihira3.db"
    jisyo_itaiji = "itaijidict4.db"
    jisyo_kanwa = "kanwadict4.db"
    jisyo_hepburn = "hepburndict3.db"
    jisyo_passport = "passportdict3.db"
    jisyo_kunrei = "kunreidict3.db"
    jisyo_halfkana = "halfkana3.db"

    def dictpath(self, dbfile: str):
        return os.path.join(self.data_path, dbfile)


Configurations = Configurations()


class Ch:
    space = 0x20
    at_mark = 0x40
    alphabet_A = 0x41
    alphabet_Z = 0x5A
    square_bra = 0x5B
    back_quote = 0x60
    alphabet_a = 0x61
    alphabet_z = 0x7A
    bracket_bra = 0x7B
    tilda = 0x7E
    delete = 0x7F
    ideographic_space = 0x3000
    postal_mark_face = 0x3020
    wavy_dash = 0x3030
    ideographic_half_fill_space = 0x303F
    greece_Alpha = 0x0391
    greece_Rho = 0x30A1
    greece_Sigma = 0x30A3
    greece_Omega = 0x03A9
    greece_alpha = 0x03B1
    greece_omega = 0x03C9
    cyrillic_A = 0x0410
    cyrillic_E = 0x0401
    cyrillic_e = 0x0451
    cyrillic_ya = 0x044F
    zenkaku_exc_mark = 0xFF01
    zenkaku_slash_mark = 0xFF0F
    zenkaku_number_zero = 0xFF10
    zenkaku_number_nine = 0xFF1A
    zenkaku_A = 0xFF21
    zenkaku_a = 0xFF41
    endmark = ")]!,.,\u3001\u3002\uff1f\uff10\uff1e\uff1c"
    long_symbols = "\u30FC\u2015\u2212\uFF70"  # "ー  ―  −  ｰ "
    # _UNCHECKED_LONG_SYMBOLS: str = "\u002D\u2010\u2011\u2013\u2014" # "-  ‐ ‑ – —"


Ch = Ch()


class Convert_Tables:
    """
    convert symbols to alphabet
    based on Original KAKASI's EUC_JP - alphabet converter table
    --------------------------------------------------------------------------
     a1 a0 | 　 、 。 ， ． ・ ： ； ？ ！ ゛ ゜ ´ ｀ ¨
             " ",",",".",",",".",".",":",";","?",
             "!","\"","(maru)","'","`","..",
     a1 b0 | ＾ ￣ ＿ ヽ ヾ ゝ ゞ 〃 仝 々 〆 〇 ー ― ‐ ／
           "~","~","_","(kurikaesi)","(kurikaesi)","(kurikaesi)",
           "(kurikaesi)","(kurikaesi)","(kurikaesi)","(kurikaesi)",
           "sime","(maru)","^","-","-","/",
     a1 c0 | ＼ ～ ∥ ｜ … ‥ ‘ ’ “ ” （ ） 〔 〕 ［ ］
          "\\","~","||","|","...","..","`","'","\"","\"","(",")","[","]","[","]",
          "{","}","<",">","<<",">>","(",")","(",")","(",")","+","-","+-","X",
     a1 d0 | ｛ ｝ 〈 〉 《 》 「 」 『 』 【 】 ＋ － ± ×

     a1 e0 | ÷ ＝ ≠ ＜ ＞ ≦ ≧ ∞ ∴ ♂ ♀ ° ′ ″ ℃ ￥
          "/","=","!=","<",">","<=",">=","(kigou)","...",
          "(osu)","(mesu)","(do)","'","\"","(Sessi)","\\",
     a1 f0 | ＄ ￠ ￡ ％ ＃ ＆ ＊ ＠ § ☆ ★ ○ ● ◎ ◇
          "$","(cent)","(pound)","%","#","&","*","@",
          "(setu)","(hosi)","(hosi)","(maru)","(maru)","(maru)","(diamond)"
    ---------------------------------------------------------------------------

    ----------------------------------------------------------
     a2 a0 | ◆ □ ■ △ ▲ ▽ ▼ ※ 〒 → ← ↑ ↓ 〓
     a2 b0 | ∈ ∋ ⊆ ⊇ ⊂ ⊃ a2 c0 | ∪ ∩ ∧ ∨ ￢ ⇒ ⇔ ∀
     a2 d0 | ∃ ∠ ⊥ ⌒ ∂
     a2 e0 | ∇ ≡ ≒ ≪ ≫ √ ∽ ∝ ∵ ∫ ∬
     a2 f0 | Å ‰ ♯ ♭ ♪ † ‡ ¶ ◯
    ----------------------------------------------------------

    Greek convertion table
    ----------------------------------------------------------
       "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
       "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
       "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega",
       "", "", "", "", "", "", "", "",
       "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
       "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
       "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"
    ----------------------------------------------------------
    """

    # U3000 - 301F
    # \u3000、。〃〄〇〆々〈〉《》「」『』【】〒〓〔〕〖〗〘〙
    # 〚〛〜〝〞〟〠
    symbol_table_1 = [
        " ",
        ",",
        ".",
        '"',
        "(kigou)",
        "(kurikaesi)",
        "(sime)",
        "(maru)",
        "<",
        ">",
        "<<",
        ">>",
        "(",
        ")",
        "(",
        ")",
        "(",
        ")",
        "(kigou)",
        "(geta)",
        "(",
        ")",
        "(",
        ")",
        "(",
        ")",
        "(",
        ")",
        "~",
        "(kigou)",
        '"',
        "(kigou)",
        "(kigou)",
    ]
    # U3030 - 3040
    # 〰〱〲〳〴〵〶〷〼〽〾〿
    symbol_table_2 = [
        "-",
        "(kurikaesi)",
        "(kurikaesi)",
        "(kurikaesi)",
        "(kurikaesi)",
        "(kurikaesi)",
        "(kigou)",
        "XX",
        None,
        None,
        None,
        None,
        "(masu)",
        "(kurikaesi)",
        " ",
        " ",
    ]
    # U0391-03A9
    symbol_table_3 = [
        "Alpha",
        "Beta",
        "Gamma",
        "Delta",
        "Epsilon",
        "Zeta",
        "Eta",
        "Theta",
        "Iota",
        "Kappa",
        "Lambda",
        "Mu",
        "Nu",
        "Xi",
        "Omicron",
        "Pi",
        "Rho",
        None,
        "Sigma",
        "Tau",
        "Upsilon",
        "Phi",
        "Chi",
        "Psi",
        "Omega",
    ]
    # U03B1-03C9
    symbol_table_4 = [
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "zeta",
        "eta",
        "theta",
        "iota",
        "kappa",
        "lambda",
        "mu",
        "nu",
        "xi",
        "omicron",
        "pi",
        "rho",
        "final sigma",
        "sigma",
        "tau",
        "upsilon",
        "phi",
        "chi",
        "psi",
        "omega",
    ]
    # UFF01-FF0F
    symbol_table_5 = [
        "!",
        '"',
        "#",
        "$",
        "%",
        "&",
        "'",
        "(",
        ")",
        "*",
        "+",
        ",",
        "-",
        ".",
        "/",
    ]
    # cyriilic
    cyrillic_table = {  # basic cyrillic characters
        "\u0410": "A",
        "\u0411": "B",
        "\u0412": "V",  # АБВ
        "\u0413": "G",
        "\u0414": "D",
        "\u0415": "E",  # ГДЕ
        "\u0401": "E",
        "\u0416": "Zh",
        "\u0417": "Z",  # ЁЖЗ
        "\u0418": "I",
        "\u0419": "Y",
        "\u041a": "K",  # ИЙК
        "\u041b": "L",
        "\u041c": "M",
        "\u041d": "N",  # ЛМН
        "\u041e": "O",
        "\u041f": "P",
        "\u0420": "R",  # ОПР
        "\u0421": "S",
        "\u0422": "T",
        "\u0423": "U",  # СТУ
        "\u0424": "F",
        "\u0425": "H",
        "\u0426": "Ts",  # ФХЦ
        "\u0427": "Ch",
        "\u0428": "Sh",
        "\u0429": "Sch",  # ЧШЩ
        "\u042a": "",
        "\u042b": "Y",
        "\u042c": "",  # ЪЫЬ
        "\u042d": "E",
        "\u042e": "Yu",
        "\u042f": "Ya",  # ЭЮЯ
        "\u0430": "a",
        "\u0431": "b",
        "\u0432": "v",  # абв
        "\u0433": "g",
        "\u0434": "d",
        "\u0435": "e",  # где
        "\u0451": "e",
        "\u0436": "zh",
        "\u0437": "z",  # ёжз
        "\u0438": "i",
        "\u0439": "y",
        "\u043a": "k",  # ийк
        "\u043b": "l",
        "\u043c": "m",
        "\u043d": "n",  # лмн
        "\u043e": "o",
        "\u043f": "p",
        "\u0440": "r",  # опр
        "\u0441": "s",
        "\u0442": "t",
        "\u0443": "u",  # сту
        "\u0444": "f",
        "\u0445": "h",
        "\u0446": "ts",  # фхц
        "\u0447": "ch",
        "\u0448": "sh",
        "\u0449": "sch",  # чшщ
        "\u044a": "",
        "\u044b": "y",
        "\u044c": "",  # ъыь
        "\u044d": "e",
        "\u044e": "yu",
        "\u044f": "ya",  # эюя
    }

    alpha_table_1 = [
        "\u3000",
        "\uff01",
        "\uff02",
        "\uff03",
        "\uff04",
        "\uff05",
        "\uff06",
        "\uff07",
        "\uff08",
        "\uff09",
        "\uff0a",
        "\uff0b",
        "\uff0c",
        "\uff0d",
        "\uff0e",
        "\uff0f",  # ！＂＃＄％＆＇（）＊＋，－．／
        "\uff10",
        "\uff11",
        "\uff12",
        "\uff13",
        "\uff14",
        "\uff15",
        "\uff16",
        "\uff17",
        "\uff18",
        "\uff19",  # ０...９
        "\uff1a",
        "\uff1b",
        "\uff1c",
        "\uff1d",
        "\uff1e",
        "\uff1f",
        "\uff20",
    ]  # ：；＜＝＞？＠
    alpha_table_2 = [
        "\uff3b",
        "\uff3c",
        "\uff3d",
        "\uff3e",
        "\uff3f",
        "\uff40",
    ]  # ［＼］＾＿｀
    alpha_table_3 = ["\uff5b", "\uff5c", "\uff5d", "\uff5e"]  # ｛｜｝～


Convert_Tables = Convert_Tables()
