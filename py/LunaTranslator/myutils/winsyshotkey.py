import queue
import time

import _thread as thread
import windows


unique_int = 0


class registerException(Exception):
    pass


import threading


class SystemHotkey:
    hk_ref = {}
    keybinds = {}
    _error = False
    waitforregist = threading.Lock()
    changedlock = threading.Lock()

    def register(self, hotkey, callback):
        masks, keycode = hotkey
        self._error = False

        def nt_register():
            global unique_int
            unique_int += 1
            self.changedlock.acquire()
            self.hk_ref[unique_int] = hotkey
            self.changedlock.release()
            if not windows.RegisterHotKey(None, unique_int, masks, keycode):
                self._error = True
            self.waitforregist.release()

        self.hk_action_queue.put(lambda: nt_register())
        self.waitforregist.acquire()
        if self._error:
            raise registerException()
        self.keybinds[(hotkey)] = callback

    def unregister(self, hotkey):

        def nt_unregister(hk_to_remove):
            _use = None
            self.changedlock.acquire()
            for key, value in self.hk_ref.items():
                if value == hk_to_remove:
                    _use = key
                    break
            if _use:
                del self.hk_ref[_use]
                windows.UnregisterHotKey(None, _use)
            self.changedlock.release()

        self.hk_action_queue.put(lambda: nt_unregister(hotkey))
        self.changedlock.acquire()
        if hotkey in self.keybinds:
            del self.keybinds[hotkey]
        self.changedlock.release()

    def __init__(self, check_queue_interval=0.001):
        self.waitforregist.acquire()
        self.check_queue_interval = check_queue_interval
        self.hk_action_queue = queue.Queue()

        thread.start_new_thread(
            self._nt_wait,
            (),
        )

    def _nt_wait(self):
        msg = windows.MSG()
        while 1:
            try:
                remove_or_add = self.hk_action_queue.get(block=False)
                # 我tm明白了，必须在这里用queue来regist，不然regist和peekmessage不在一个线程。
            except queue.Empty:
                pass
            else:
                remove_or_add()
            if windows.PeekMessageA(windows.pointer(msg), 0, 0, 0, windows.PM_REMOVE):
                if msg.message == windows.WM_HOTKEY:
                    self.changedlock.acquire()
                    hotkey = self.hk_ref[msg.wParam][0], self.hk_ref[msg.wParam][1]
                    if hotkey in self.keybinds:
                        threading.Thread(target=self.keybinds[(hotkey)]).start()
                    self.changedlock.release()
            time.sleep(self.check_queue_interval)
