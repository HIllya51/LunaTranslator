from myutils.config import globalconfig
from threading import Thread
from queue import Queue


class Base:
    @property
    def config(self):
        return globalconfig["textoutputer"][self.classname]

    def dispatch(self, text):
        pass

    def init(self):
        pass

    def __init__(self, classname):
        self.classname = classname
        self.queue = Queue()
        self.init()
        Thread(target=self.dothread).start()

    def dothread(self):
        while True:
            text = self.queue.get()
            self.dispatch(text)

    def puttask(self, text):
        self.queue.put(text)
