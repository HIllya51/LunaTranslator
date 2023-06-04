from utils.config import _TR

class ArgsEmptyExc(Exception):
    def __init__(self,valuelist) -> None:
        super().__init__(' , '.join(valuelist)+_TR("不能为空"))
