from myutils.utils import selectdebugfile, checkmd5reloadmodule
import gobject


class Process:
    @staticmethod
    def get_setting_window(_):
        return selectdebugfile(gobject.getconfig("myprocess.py"))

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
        isnew, module = checkmd5reloadmodule(gobject.getconfig("myprocess.py"), "myprocess")
        if not isnew:
            return
        if module:
            self.internal = module.Process()
