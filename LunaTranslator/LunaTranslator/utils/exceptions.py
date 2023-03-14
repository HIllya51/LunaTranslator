class ArgsEmptyExc(Exception):
    def __init__(self,valuelist) -> None:
        super().__init__(' and '.join(valuelist)+" can't be empty")
class TimeOut(Exception):
     pass