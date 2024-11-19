def callLunaHost(text, split):
    try:
        import ctypes

        try:
            luna_internal_renpy_call_host = ctypes.CDLL(
                "LunaHook64"
            ).luna_internal_renpy_call_host
        except:
            luna_internal_renpy_call_host = ctypes.CDLL(
                "LunaHook32"
            ).luna_internal_renpy_call_host
        luna_internal_renpy_call_host.argstype = ctypes.c_wchar_p, ctypes.c_int
        luna_internal_renpy_call_host.restype = ctypes.c_wchar_p

        try:
            _text = text.decode("utf8")
        except:
            _text = text
        text = luna_internal_renpy_call_host(_text, split)
    except:
        pass
    return text


def callLunaIsUsingEmbed(split):
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

        return luna_internal_renpy_call_is_embed_using(split, True)
    except:
        return False


try:
    # 6.1.0
    import renpy

    def hook_initT0(original_init):

        def new_init(self, *args, **kwargs):
            changed = False
            if isinstance(args[0], list):
                trs = []
                for _ in args[0]:
                    _n = callLunaHost(_, 1)
                    if _n != _:
                        changed = True
                    trs += [_n]
            else:
                trs = callLunaHost(args[0], 1)
                if args[0] != trs:
                    changed = True

            if changed and callLunaIsUsingEmbed(1):
                args = (trs,) + args[1:]
                if "text" in kwargs:
                    kwargs["text"] = trs

            original_init(self, *args, **kwargs)

        return new_init

    if "original_Text_init_hook" not in globals():
        original_Text_init_hook = renpy.text.text.Text.__init__

    renpy.text.text.Text.__init__ = hook_initT0(original_Text_init_hook)

    def hook_init_renderT0(original):
        def new_init(self, *args, **kwargs):
            if not hasattr(self, "LunaHooked"):
                changed = False
                if isinstance(self.text, list):
                    trs = []
                    for _ in self.text:
                        _n = callLunaHost(_, 2)
                        if _n != _:
                            changed = True
                        trs += [_n]
                else:
                    trs = callLunaHost(self.text, 2)
                    if self.text != trs:
                        changed = True
                if changed and callLunaIsUsingEmbed(2):
                    self.set_text(trs)
                    self.LunaHooked = True
            return original(self, *args, **kwargs)

        return new_init

    if "original_hook_init_renderT0" not in globals():
        original_hook_init_renderT0 = renpy.text.text.Text.render

    renpy.text.text.Text.render = hook_init_renderT0(original_hook_init_renderT0)
except:
    pass
try:
    # 4.0
    import renpy

    def hook_initT3(original_init):
        def new_init(self, *args, **kwargs):
            trs = callLunaHost(str(args[0]), 3)
            if callLunaIsUsingEmbed(3):
                args = (trs,) + args[1:]
            original_init(self, *args, **kwargs)

        return new_init

    if "original_Text_init_hookT3" not in globals():
        original_Text_init_hookT3 = renpy.exports.Text.__init__

    renpy.exports.Text.__init__ = hook_initT3(original_Text_init_hookT3)
except:
    pass
