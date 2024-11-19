def callLunaHostFont():
    try:
        import ctypes

        try:
            luna_internal_renpy_get_font = ctypes.CDLL(
                "LunaHook64"
            ).luna_internal_renpy_get_font
        except:
            luna_internal_renpy_get_font = ctypes.CDLL(
                "LunaHook32"
            ).luna_internal_renpy_get_font
        luna_internal_renpy_get_font.restype = ctypes.c_wchar_p
        return luna_internal_renpy_get_font()
    except:
        return None


def callLunaIsUsingEmbed_nosplit():
    try:
        import ctypes

        try:
            luna_internal_renpy_call_is_embed_using = ctypes.CDLL(
                "LunaHook64"
            ).luna_internal_renpy_call_is_embed_using
        except:
            luna_internal_renpy_call_is_embed_using = ctypes.CDLL(
                "LunaHook32"
            ).luna_internal_renpy_call_is_embed_using
        luna_internal_renpy_call_is_embed_using.argstype = ctypes.c_int, ctypes.c_bool
        luna_internal_renpy_call_is_embed_using.restype = ctypes.c_bool

        return luna_internal_renpy_call_is_embed_using(0, False)
    except:
        return False


try:
    import os
    import renpy

    def hook_renpy_text_font_get_font_init(original):
        def new_init(*args, **kwargs):
            # ctypes.windll.user32.MessageBoxW(None, str(kwargs), str(args), 0)
            if callLunaIsUsingEmbed_nosplit():
                font = callLunaHostFont()
                if font and font != "" and os.path.exists(font):
                    font = font.replace(
                        "\\", "/"
                    )  # 不知道为什么，用\会报错，但之前写死C:\Windows\Fonts\msyh.ttc时就没事
                    args = (font,) + args[1:]
                    if "fn" in kwargs:
                        kwargs["fn"] = font
            return original(*args, **kwargs)

        return new_init

    if "original_renpy_text_font_get_font" not in globals():
        original_renpy_text_font_get_font = renpy.text.font.get_font
    renpy.text.font.get_font = hook_renpy_text_font_get_font_init(
        original_renpy_text_font_get_font
    )

except:
    pass
