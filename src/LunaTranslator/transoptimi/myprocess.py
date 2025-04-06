from myutils.utils import selectdebugfile, checkmd5reloadmodule


class Process:
    @staticmethod
    def get_setting_window(_):
        return selectdebugfile("userconfig/myprocess.py")

    def process_after(self, res, contenxt):
        self.mayreinit()
        if not self.internal:
            return res
        return self.internal.process_after(res, contenxt)

    def process_before(self, s):

        self.mayreinit()
        if not self.internal:
            return s, None
        return self.internal.process_before(s)

    def __init__(self) -> None:
        self.internal = None
        self.mayreinit()

    def mayreinit(self):
        isnew, module = checkmd5reloadmodule("userconfig/myprocess.py", "myprocess")
        if not isnew:
            return
        if module:
            self.internal = module.Process()
