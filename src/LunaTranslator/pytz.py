import datetime

ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)
from datetime import datetime, tzinfo


class BaseTzInfo(tzinfo):
    # Overridden in subclass
    _utcoffset = None
    _tzname = None
    zone = None

    def __str__(self):
        return self.zone


def _UTC():
    return utc


class UTC(BaseTzInfo):
    """UTC

    Optimized UTC implementation. It unpickles using the single module global
    instance defined beneath this class declaration.
    """

    zone = "UTC"

    _utcoffset = ZERO
    _dst = ZERO
    _tzname = zone

    def fromutc(self, dt: datetime):
        if dt.tzinfo is None:
            return self.localize(dt)
        return super(utc.__class__, self).fromutc(dt)

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

    def __reduce__(self):
        return _UTC, ()

    def localize(self, dt: datetime, is_dst=False):
        """Convert naive time to local time"""
        if dt.tzinfo is not None:
            raise ValueError("Not naive datetime (tzinfo is already set)")
        return dt.replace(tzinfo=self)

    def normalize(self, dt: datetime, is_dst=False):
        """Correct the timezone information on the given datetime"""
        if dt.tzinfo is self:
            return dt
        if dt.tzinfo is None:
            raise ValueError("Naive time - no tzinfo set")
        return dt.astimezone(self)

    def __repr__(self):
        return "<UTC>"

    def __str__(self):
        return "UTC"


UTC = utc = UTC()  # UTC is a singleton


def timezone(zone):
    if zone == "UTC":
        return utc
    else:
        raise Exception(zone)
