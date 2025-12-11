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
        luna_internal_renpy_get_font.argtypes = ctypes.POINTER(
            ctypes.c_wchar_p
        ), ctypes.POINTER(ctypes.c_float)
        font = ctypes.c_wchar_p()
        relsize = ctypes.c_float()
        luna_internal_renpy_get_font(ctypes.pointer(font), ctypes.pointer(relsize))
        return font.value, relsize.value
    except:
        return None, 1.0


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
                font, relsize = callLunaHostFont()
                if font and font != "" and os.path.exists(font):
                    font = font.replace(
                        "\\", "/"
                    )  # 不知道为什么，用\会报错，但之前写死C:\Windows\Fonts\msyh.ttc时就没事
                    args = (font,) + args[1:]
                    if "fn" in kwargs:
                        kwargs["fn"] = font
                if relsize != 1.0:
                    args = (
                        args[:1]
                        + (max(min(args[1], 1), int(args[1] * relsize)),)
                        + args[2:]
                    )
                    if "size" in kwargs:
                        kwargs["size"] = max(
                            min(kwargs["size"], 1), int(kwargs["size"] * relsize)
                        )
            return original(*args, **kwargs)

        return new_init

    if "original_renpy_text_font_get_font" not in globals():
        original_renpy_text_font_get_font = renpy.text.font.get_font
    renpy.text.font.get_font = hook_renpy_text_font_get_font_init(
        original_renpy_text_font_get_font
    )

except:
    pass
