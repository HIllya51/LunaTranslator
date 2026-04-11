from qtsymbols import QEvent

DarkLightChanged = QEvent.Type.User + 1
DarkLightSettingChanged = DarkLightChanged + 1


class DarkLightChangedEvent(QEvent):
    def __init__(self, isdark: bool):
        super().__init__(DarkLightChanged)
        self.__isdark = isdark

    def isdark(self):
        return self.__isdark


class DarkLightSettingChangedEvent(QEvent):
    def __init__(self, darklight: int):
        super().__init__(DarkLightSettingChanged)
        self.__darklight = darklight

    def darklight(self):
        return self.__darklight


TransparentChanged = DarkLightSettingChanged + 1


class TransparentChangedEvent(QEvent):
    def __init__(self, transparent_value: int):
        super().__init__(DarkLightChanged)
        self.__ts = transparent_value

    def transparent_value(self):
        return self.__ts
