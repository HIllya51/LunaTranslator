from ..base import *
from .time_helpers import *

TZ_OFFSET = (time.altzone // 3600)
ABS_OFFSET = abs(TZ_OFFSET)
TZ_NAME = time.tzname[1]
ISO_FORMAT = '%s-%s-%sT%s:%s:%s.%sZ'


@Js
def Date(year, month, date, hours, minutes, seconds, ms):
    return now().to_string()


Date.Class = 'Date'


def now():
    return PyJsDate(int(time.time() * 1000), prototype=DatePrototype)


@Js
def UTC(year, month, date, hours, minutes, seconds, ms):  # todo complete this
    args = arguments
    y = args[0].to_number()
    m = args[1].to_number()
    l = len(args)
    dt = args[2].to_number() if l > 2 else Js(1)
    h = args[3].to_number() if l > 3 else Js(0)
    mi = args[4].to_number() if l > 4 else Js(0)
    sec = args[5].to_number() if l > 5 else Js(0)
    mili = args[6].to_number() if l > 6 else Js(0)
    if not y.is_nan() and 0 <= y.value <= 99:
        y = y + Js(1900)
    return TimeClip(MakeDate(MakeDay(y, m, dt), MakeTime(h, mi, sec, mili)))


@Js
def parse(string):
    return PyJsDate(
        TimeClip(parse_date(string.to_string().value)),
        prototype=DatePrototype)


Date.define_own_property('now', {
    'value': Js(now),
    'enumerable': False,
    'writable': True,
    'configurable': True
})

Date.define_own_property('parse', {
    'value': parse,
    'enumerable': False,
    'writable': True,
    'configurable': True
})

Date.define_own_property('UTC', {
    'value': UTC,
    'enumerable': False,
    'writable': True,
    'configurable': True
})


class PyJsDate(PyJs):
    Class = 'Date'
    extensible = True

    def __init__(self, value, prototype=None):
        self.value = value
        self.own = {}
        self.prototype = prototype

    # todo fix this problematic datetime part
    def to_local_dt(self):
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(
            seconds=UTCToLocal(self.value) // 1000)

    def to_utc_dt(self):
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(
            seconds=self.value // 1000)

    def local_strftime(self, pattern):
        if self.value is NaN:
            return 'Invalid Date'
        try:
            dt = self.to_local_dt()
        except:
            raise MakeError(
                'TypeError',
                'unsupported date range. Will fix in future versions')
        try:
            return dt.strftime(pattern)
        except:
            raise MakeError(
                'TypeError',
                'Could not generate date string from this date (limitations of python.datetime)'
            )

    def utc_strftime(self, pattern):
        if self.value is NaN:
            return 'Invalid Date'
        try:
            dt = self.to_utc_dt()
        except:
            raise MakeError(
                'TypeError',
                'unsupported date range. Will fix in future versions')
        try:
            return dt.strftime(pattern)
        except:
            raise MakeError(
                'TypeError',
                'Could not generate date string from this date (limitations of python.datetime)'
            )


def parse_date(py_string):  # todo support all date string formats
    date_formats = (
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%b %d %Y",
    )
    # Supports these hour formats and with or hour.
    hour_formats = (
        "T%H:%M:%S.%f",
        "T%H:%M:%S",
    ) + ('',)
    # Supports with or without Z indicator.
    z_formats = ("Z",) + ('',)
    supported_formats = [
        d + t + z
        for d in date_formats
        for t in hour_formats
        for z in z_formats
    ]
    for date_format in supported_formats:
        try:
            dt = datetime.datetime.strptime(py_string, date_format)
        except ValueError:
            continue
        else:
            return MakeDate(
                MakeDay(Js(dt.year), Js(dt.month - 1), Js(dt.day)),
                MakeTime(
                    Js(dt.hour), Js(dt.minute), Js(dt.second),
                    Js(dt.microsecond // 1000)))

    raise MakeError(
        'TypeError',
        'Could not parse date %s - unsupported date format. Currently only supported formats are RFC3339 utc, ISO Date, Short Date, and Long Date. Sorry!'
        % py_string)


def date_constructor(*args):
    if len(args) >= 2:
        return date_constructor2(*args)
    elif len(args) == 1:
        return date_constructor1(args[0])
    else:
        return date_constructor0()


def date_constructor0():
    return now()


def date_constructor1(value):
    v = value.to_primitive()
    if v._type() == 'String':
        v = parse_date(v.value)
    else:
        v = v.to_int()
    return PyJsDate(TimeClip(v), prototype=DatePrototype)


def date_constructor2(*args):
    y = args[0].to_number()
    m = args[1].to_number()
    l = len(args)
    dt = args[2].to_number() if l > 2 else Js(1)
    h = args[3].to_number() if l > 3 else Js(0)
    mi = args[4].to_number() if l > 4 else Js(0)
    sec = args[5].to_number() if l > 5 else Js(0)
    mili = args[6].to_number() if l > 6 else Js(0)
    if not y.is_nan() and 0 <= y.value <= 99:
        y = y + Js(1900)
    t = TimeClip(
        LocalToUTC(MakeDate(MakeDay(y, m, dt), MakeTime(h, mi, sec, mili))))
    return PyJsDate(t, prototype=DatePrototype)


Date.create = date_constructor

DatePrototype = PyJsDate(float('nan'), prototype=ObjectPrototype)


def check_date(obj):
    if obj.Class != 'Date':
        raise MakeError('TypeError', 'this is not a Date object')


class DateProto:
    def toString():
        check_date(this)
        if this.value is NaN:
            return 'Invalid Date'
        offset = (UTCToLocal(this.value) - this.value) // msPerHour
        return this.local_strftime(
            '%a %b %d %Y %H:%M:%S GMT') + '%s00 (%s)' % (pad(
                offset, 2, True), GetTimeZoneName(this.value))

    def toDateString():
        check_date(this)
        return this.local_strftime('%d %B %Y')

    def toTimeString():
        check_date(this)
        return this.local_strftime('%H:%M:%S')

    def toLocaleString():
        check_date(this)
        return this.local_strftime('%d %B %Y %H:%M:%S')

    def toLocaleDateString():
        check_date(this)
        return this.local_strftime('%d %B %Y')

    def toLocaleTimeString():
        check_date(this)
        return this.local_strftime('%H:%M:%S')

    def valueOf():
        check_date(this)
        return this.value

    def getTime():
        check_date(this)
        return this.value

    def getFullYear():
        check_date(this)
        if this.value is NaN:
            return NaN
        return YearFromTime(UTCToLocal(this.value))

    def getUTCFullYear():
        check_date(this)
        if this.value is NaN:
            return NaN
        return YearFromTime(this.value)

    def getMonth():
        check_date(this)
        if this.value is NaN:
            return NaN
        return MonthFromTime(UTCToLocal(this.value))

    def getDate():
        check_date(this)
        if this.value is NaN:
            return NaN
        return DateFromTime(UTCToLocal(this.value))

    def getUTCMonth():
        check_date(this)
        if this.value is NaN:
            return NaN
        return MonthFromTime(this.value)

    def getUTCDate():
        check_date(this)
        if this.value is NaN:
            return NaN
        return DateFromTime(this.value)

    def getDay():
        check_date(this)
        if this.value is NaN:
            return NaN
        return WeekDay(UTCToLocal(this.value))

    def getUTCDay():
        check_date(this)
        if this.value is NaN:
            return NaN
        return WeekDay(this.value)

    def getHours():
        check_date(this)
        if this.value is NaN:
            return NaN
        return HourFromTime(UTCToLocal(this.value))

    def getUTCHours():
        check_date(this)
        if this.value is NaN:
            return NaN
        return HourFromTime(this.value)

    def getMinutes():
        check_date(this)
        if this.value is NaN:
            return NaN
        return MinFromTime(UTCToLocal(this.value))

    def getUTCMinutes():
        check_date(this)
        if this.value is NaN:
            return NaN
        return MinFromTime(this.value)

    def getSeconds():
        check_date(this)
        if this.value is NaN:
            return NaN
        return SecFromTime(UTCToLocal(this.value))

    def getUTCSeconds():
        check_date(this)
        if this.value is NaN:
            return NaN
        return SecFromTime(this.value)

    def getMilliseconds():
        check_date(this)
        if this.value is NaN:
            return NaN
        return msFromTime(UTCToLocal(this.value))

    def getUTCMilliseconds():
        check_date(this)
        if this.value is NaN:
            return NaN
        return msFromTime(this.value)

    def getTimezoneOffset():
        check_date(this)
        if this.value is NaN:
            return NaN
        return (this.value - UTCToLocal(this.value)) // 60000

    def setTime(time):
        check_date(this)
        this.value = TimeClip(time.to_number().to_int())
        return this.value

    def setMilliseconds(ms):
        check_date(this)
        t = UTCToLocal(this.value)
        tim = MakeTime(
            Js(HourFromTime(t)), Js(MinFromTime(t)), Js(SecFromTime(t)), ms)
        u = TimeClip(LocalToUTC(MakeDate(Day(t), tim)))
        this.value = u
        return u

    def setUTCMilliseconds(ms):
        check_date(this)
        t = this.value
        tim = MakeTime(
            Js(HourFromTime(t)), Js(MinFromTime(t)), Js(SecFromTime(t)), ms)
        u = TimeClip(MakeDate(Day(t), tim))
        this.value = u
        return u

    def setSeconds(sec, ms=None):
        check_date(this)
        t = UTCToLocal(this.value)
        s = sec.to_number()
        if not ms is None: milli = Js(msFromTime(t))
        else: milli = ms.to_number()
        date = MakeDate(
            Day(t), MakeTime(Js(HourFromTime(t)), Js(MinFromTime(t)), s, milli))
        u = TimeClip(LocalToUTC(date))
        this.value = u
        return u

    def setUTCSeconds(sec, ms=None):
        check_date(this)
        t = this.value
        s = sec.to_number()
        if not ms is None: milli = Js(msFromTime(t))
        else: milli = ms.to_number()
        date = MakeDate(
            Day(t), MakeTime(Js(HourFromTime(t)), Js(MinFromTime(t)), s, milli))
        v = TimeClip(date)
        this.value = v
        return v

    def setMinutes(min, sec=None, ms=None):
        check_date(this)
        t = UTCToLocal(this.value)
        m = min.to_number()
        if not sec is None: s = Js(SecFromTime(t))
        else: s = sec.to_number()
        if not ms is None: milli = Js(msFromTime(t))
        else: milli = ms.to_number()
        date = MakeDate(Day(t), MakeTime(Js(HourFromTime(t)), m, s, milli))
        u = TimeClip(LocalToUTC(date))
        this.value = u
        return u

    def setUTCMinutes(min, sec=None, ms=None):
        check_date(this)
        t = this.value
        m = min.to_number()
        if not sec is None: s = Js(SecFromTime(t))
        else: s = sec.to_number()
        if not ms is None: milli = Js(msFromTime(t))
        else: milli = ms.to_number()
        date = MakeDate(Day(t), MakeTime(Js(HourFromTime(t)), m, s, milli))
        v = TimeClip(date)
        this.value = v
        return v

    def setHours(hour, min=None, sec=None, ms=None):
        check_date(this)
        t = UTCToLocal(this.value)
        h = hour.to_number()
        if not min is None: m = Js(MinFromTime(t))
        else: m = min.to_number()
        if not sec is None: s = Js(SecFromTime(t))
        else: s = sec.to_number()
        if not ms is None: milli = Js(msFromTime(t))
        else: milli = ms.to_number()
        date = MakeDate(Day(t), MakeTime(h, m, s, milli))
        u = TimeClip(LocalToUTC(date))
        this.value = u
        return u

    def setUTCHours(hour, min=None, sec=None, ms=None):
        check_date(this)
        t = this.value
        h = hour.to_number()
        if not min is None: m = Js(MinFromTime(t))
        else: m = min.to_number()
        if not sec is None: s = Js(SecFromTime(t))
        else: s = sec.to_number()
        if not ms is None: milli = Js(msFromTime(t))
        else: milli = ms.to_number()
        date = MakeDate(Day(t), MakeTime(h, m, s, milli))
        v = TimeClip(date)
        this.value = v
        return v

    def setDate(date):
        check_date(this)
        t = UTCToLocal(this.value)
        dt = date.to_number()
        newDate = MakeDate(
            MakeDay(Js(YearFromTime(t)), Js(MonthFromTime(t)), dt), TimeWithinDay(t))
        u = TimeClip(LocalToUTC(newDate))
        this.value = u
        return u

    def setUTCDate(date):
        check_date(this)
        t = this.value
        dt = date.to_number()
        newDate = MakeDate(
            MakeDay(Js(YearFromTime(t)), Js(MonthFromTime(t)), dt), TimeWithinDay(t))
        v = TimeClip(newDate)
        this.value = v
        return v

    def setMonth(month, date=None):
        check_date(this)
        t = UTCToLocal(this.value)
        m = month.to_number()
        if not date is None: dt = Js(DateFromTime(t))
        else: dt = date.to_number()
        newDate = MakeDate(
            MakeDay(Js(YearFromTime(t)), m, dt), TimeWithinDay(t))
        u = TimeClip(LocalToUTC(newDate))
        this.value = u
        return u

    def setUTCMonth(month, date=None):
        check_date(this)
        t = this.value
        m = month.to_number()
        if not date is None: dt = Js(DateFromTime(t))
        else: dt = date.to_number()
        newDate = MakeDate(
            MakeDay(Js(YearFromTime(t)), m, dt), TimeWithinDay(t))
        v = TimeClip(newDate)
        this.value = v
        return v

    def setFullYear(year, month=None, date=None):
        check_date(this)
        if not this.value is NaN: t = UTCToLocal(this.value)
        else: t = 0
        y = year.to_number()
        if not month is None: m = Js(MonthFromTime(t))
        else: m = month.to_number()
        if not date is None: dt = Js(DateFromTime(t))
        else: dt = date.to_number()
        newDate = MakeDate(
            MakeDay(y, m, dt), TimeWithinDay(t))
        u = TimeClip(LocalToUTC(newDate))
        this.value = u
        return u

    def setUTCFullYear(year, month=None, date=None):
        check_date(this)
        if not this.value is NaN: t = UTCToLocal(this.value)
        else: t = 0
        y = year.to_number()
        if not month is None: m = Js(MonthFromTime(t))
        else: m = month.to_number()
        if not date is None: dt = Js(DateFromTime(t))
        else: dt = date.to_number()
        newDate = MakeDate(
            MakeDay(y, m, dt), TimeWithinDay(t))
        v = TimeClip(newDate)
        this.value = v
        return v

    def toUTCString():
        check_date(this)
        return this.utc_strftime('%d %B %Y %H:%M:%S')

    def toISOString():
        check_date(this)
        t = this.value
        year = YearFromTime(t)
        month, day, hour, minute, second, milli = pad(
            MonthFromTime(t) + 1), pad(DateFromTime(t)), pad(
                HourFromTime(t)), pad(MinFromTime(t)), pad(
                    SecFromTime(t)), pad(msFromTime(t))
        return ISO_FORMAT % (unicode(year) if 0 <= year <= 9999 else pad(
            year, 6, True), month, day, hour, minute, second, milli)

    def toJSON(key):
        o = this.to_object()
        tv = o.to_primitive('Number')
        if tv.Class == 'Number' and not tv.is_finite():
            return this.null
        toISO = o.get('toISOString')
        if not toISO.is_callable():
            raise this.MakeError('TypeError', 'toISOString is not callable')
        return toISO.call(o, ())


def pad(num, n=2, sign=False):
    '''returns n digit string representation of the num'''
    s = unicode(abs(num))
    if len(s) < n:
        s = '0' * (n - len(s)) + s
    if not sign:
        return s
    if num >= 0:
        return '+' + s
    else:
        return '-' + s


fill_prototype(DatePrototype, DateProto, default_attrs)

Date.define_own_property(
    'prototype', {
        'value': DatePrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })

DatePrototype.define_own_property('constructor', {
    'value': Date,
    'enumerable': False,
    'writable': True,
    'configurable': True
})
