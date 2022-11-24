# NOTE: t must be INT!!!
import time
import datetime
import warnings

try:
    from tzlocal import get_localzone
    LOCAL_ZONE = get_localzone()
except:  # except all problems...
    warnings.warn(
        'Please install or fix tzlocal library (pip install tzlocal) in order to make Date object work better. Otherwise I will assume DST is in effect all the time'
    )

    class LOCAL_ZONE:
        @staticmethod
        def dst(*args):
            return 1


from js2py.base import MakeError
CUM = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365)
msPerDay = 86400000
msPerYear = int(86400000 * 365.242)
msPerSecond = 1000
msPerMinute = 60000
msPerHour = 3600000
HoursPerDay = 24
MinutesPerHour = 60
SecondsPerMinute = 60
NaN = float('nan')
LocalTZA = -time.timezone * msPerSecond


def DaylightSavingTA(t):
    if t is NaN:
        return t
    try:
        return int(
            LOCAL_ZONE.dst(datetime.datetime(1970, 1, 1) + datetime.timedelta(
                seconds=t // 1000)).seconds) * 1000
    except:
        warnings.warn(
            'Invalid datetime date, assumed DST time, may be inaccurate...',
            Warning)
        return 1
        #raise MakeError('TypeError', 'date not supported by python.datetime. I will solve it in future versions')


def GetTimeZoneName(t):
    return time.tzname[DaylightSavingTA(t) > 0]


def LocalToUTC(t):
    return t - LocalTZA - DaylightSavingTA(t - LocalTZA)


def UTCToLocal(t):
    return t + LocalTZA + DaylightSavingTA(t)


def Day(t):
    return t // 86400000


def TimeWithinDay(t):
    return t % 86400000


def DaysInYear(y):
    if y % 4:
        return 365
    elif y % 100:
        return 366
    elif y % 400:
        return 365
    else:
        return 366


def DayFromYear(y):
    return 365 * (y - 1970) + (y - 1969) // 4 - (y - 1901) // 100 + (
        y - 1601) // 400


def TimeFromYear(y):
    return 86400000 * DayFromYear(y)


def YearFromTime(t):
    guess = 1970 - t // 31556908800  # msPerYear
    gt = TimeFromYear(guess)
    if gt <= t:
        while gt <= t:
            guess += 1
            gt = TimeFromYear(guess)
        return guess - 1
    else:
        while gt > t:
            guess -= 1
            gt = TimeFromYear(guess)
        return guess


def DayWithinYear(t):
    return Day(t) - DayFromYear(YearFromTime(t))


def InLeapYear(t):
    y = YearFromTime(t)
    if y % 4:
        return 0
    elif y % 100:
        return 1
    elif y % 400:
        return 0
    else:
        return 1


def MonthFromTime(t):
    day = DayWithinYear(t)
    leap = InLeapYear(t)
    if day < 31:
        return 0
    day -= leap
    if day < 59:
        return 1
    elif day < 90:
        return 2
    elif day < 120:
        return 3
    elif day < 151:
        return 4
    elif day < 181:
        return 5
    elif day < 212:
        return 6
    elif day < 243:
        return 7
    elif day < 273:
        return 8
    elif day < 304:
        return 9
    elif day < 334:
        return 10
    else:
        return 11


def DateFromTime(t):
    mon = MonthFromTime(t)
    day = DayWithinYear(t)
    return day - CUM[mon] - (1 if InLeapYear(t) and mon >= 2 else 0) + 1


def WeekDay(t):
    # 0 == sunday
    return (Day(t) + 4) % 7


def msFromTime(t):
    return t % 1000


def SecFromTime(t):
    return (t // 1000) % 60


def MinFromTime(t):
    return (t // 60000) % 60


def HourFromTime(t):
    return (t // 3600000) % 24


def MakeTime(hour, Min, sec, ms):
    # takes PyJs objects and returns t
    if not (hour.is_finite() and Min.is_finite() and sec.is_finite()
            and ms.is_finite()):
        return NaN
    h, m, s, milli = hour.to_int(), Min.to_int(), sec.to_int(), ms.to_int()
    return h * 3600000 + m * 60000 + s * 1000 + milli


def MakeDay(year, month, date):
    # takes PyJs objects and returns t
    if not (year.is_finite() and month.is_finite() and date.is_finite()):
        return NaN
    y, m, dt = year.to_int(), month.to_int(), date.to_int()
    y += m // 12
    mn = m % 12
    d = DayFromYear(y) + CUM[mn] + dt - 1 + (1 if DaysInYear(y) == 366
                                             and mn >= 2 else 0)
    return d  # ms per day


def MakeDate(day, time):
    return 86400000 * day + time


def TimeClip(t):
    if t != t or abs(t) == float('inf'):
        return NaN
    if abs(t) > 8.64 * 10**15:
        return NaN
    return int(t)
