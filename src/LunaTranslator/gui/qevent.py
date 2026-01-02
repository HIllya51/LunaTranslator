from qtsymbols import QEvent

DarkLightChanged = QEvent.Type.User + 1


class DarkLightChangedEvent(QEvent):
    def __init__(self, darklight: int, isdark: bool):
        super().__init__(DarkLightChanged)
        self.__darklight = darklight
        self.__isdark = isdark

    def isdark(self):
        return self.__isdark

    def darklight(self):
        return self.__darklight


TransparentChanged = DarkLightChanged + 1


class TransparentChangedEvent(QEvent):
    def __init__(self, transparent_value: int):
        super().__init__(DarkLightChanged)
        self.__ts = transparent_value

    def transparent_value(self):
        return self.__ts
