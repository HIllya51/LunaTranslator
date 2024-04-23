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

    def callstatuschange(self, hwnd):
        self.hwnd = hwnd
        self.changestatus(hwnd, self.full)
        self.setuistatus(self.full)

    def endX(self):
        if not self.full and self.hwnd:
            self.callstatuschange(self.hwnd)
            self.end()
            return True
        self.hasend = True
        return False

    def changestatus(self, hwnd, full):
        raise Exception

    def init(self):
        pass

    def end(self):
        pass
