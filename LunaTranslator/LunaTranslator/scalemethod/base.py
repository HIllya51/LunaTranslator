from myutils.wrapper import threader


class scalebase:
    def __init__(self, setuistatus) -> None:
        self._setuistatus = setuistatus
        self.full = True
        self.hwnd = None
        self.hasend = False
        self.init()

    def setuistatus(self, current):
        if self.hasend:
            return
        self._setuistatus(current)
        self.full = not current

    @threader
    def callstatuschange(self, hwnd):
        self.callstatuschange_(hwnd)

    def callstatuschange_(self, hwnd):
        self.hwnd = hwnd
        if self.changestatus(hwnd, self.full):
            self.setuistatus(self.full)

    @threader
    def endX(self):
        self.hasend = True
        ret = False
        if not self.full and self.hwnd:
            self.callstatuschange_(self.hwnd)
            ret = True
        self.end()

        return ret

    def changestatus(self, hwnd, full):
        raise Exception

    def init(self):
        pass

    def end(self):
        pass
