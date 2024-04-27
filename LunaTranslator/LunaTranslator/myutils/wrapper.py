import time
import random, threading
from traceback import print_exc


class stripwrapper(dict):
    def __getitem__(self, item):
        t = super().__getitem__(item)
        if type(t) == str:
            return t.strip()
        else:
            return t


def Singleton_impl(cls, behavior="activate"):
    _lock = threading.Lock()
    _instance = {}

    def _singleton(*args, **kwagrs):
        if _lock.locked():
            if cls not in _instance:  # __init__很慢，来不及放入_instance
                pass
            elif behavior == "activate":
                _instance[cls].activateWindow()
                _instance[cls].show()
            elif behavior == "close":
                _instance[cls].close()
            return
        _lock.acquire()

        class __(cls):
            Singleton_flag = 1

            def closeEvent(self, a0) -> None:
                super().closeEvent(a0)
                self.Singleton_flag = 0
                if cls not in _instance:
                    pass  # __init__没做完的时候不能deletelator
                else:
                    for child in self.children():
                        if hasattr(child, "Singleton_flag"):
                            child.close()
                    self.deleteLater()
                    _instance.pop(cls)
                _lock.release()

        _inst = __(*args, **kwagrs)
        if _inst.Singleton_flag:
            _instance[cls] = _inst
        return _inst

    return _singleton


def Singleton(cls):
    return Singleton_impl(cls, behavior="activate")


def Singleton_close(cls):
    return Singleton_impl(cls, behavior="close")


def retryer(**kw):
    def wrapper(func):
        def _wrapper(*args, **kwargs):
            for _ in range(kw["trytime"]):

                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    print_exc()
                    time.sleep(random.randint(2, min(2 ** (_ + 2), 32)))
                    # print('重试次数：',_+1)

        return _wrapper

    return wrapper


def threader(func):
    def _wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()

    return _wrapper


def trypass(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            pass

    return _wrapper


def tryprint(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print_exc()

    return _wrapper


def timer(func):
    def _wrapper(*args, **kwargs):
        t = time.time()
        res = func(*args, **kwargs)
        print(time.time() - t)
        return res

    return _wrapper
