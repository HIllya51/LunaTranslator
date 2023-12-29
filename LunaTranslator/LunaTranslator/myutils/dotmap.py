from __future__ import print_function
from collections import OrderedDict
try:
    from collections.abc import MutableMapping, Iterable
except ImportError:
    from collections import MutableMapping, Iterable
from json import dumps
from pprint import pprint
from sys import version_info
from inspect import ismethod

# for debugging
def here(item=None):
    out = 'here'
    if item != None:
        out += '({})'.format(item)
    print(out)

__all__ = ['DotMap']

class DotMap(MutableMapping, OrderedDict):
    def __init__(self, *args, **kwargs):
        self._map = OrderedDict()
        self._dynamic = kwargs.pop('_dynamic', True)
        self._prevent_method_masking = kwargs.pop('_prevent_method_masking', False)
        
        _key_convert_hook = kwargs.pop('_key_convert_hook', None)
        trackedIDs = kwargs.pop('_trackedIDs', {})

        if args:
            d = args[0]
            # for recursive assignment handling
            trackedIDs[id(d)] = self

            src = []
            if isinstance(d, MutableMapping):
                src = self.__call_items(d)
            elif isinstance(d, Iterable):
                src = d

            for k,v in src:
                if self._prevent_method_masking and k in reserved_keys:
                    raise KeyError('"{}" is reserved'.format(k))
                if _key_convert_hook:
                    k = _key_convert_hook(k)
                if isinstance(v, dict):
                    idv = id(v)
                    if idv in trackedIDs:
                        v = trackedIDs[idv]
                    else:
                        trackedIDs[idv] = v
                        v = self.__class__(v, _dynamic=self._dynamic, _prevent_method_masking = self._prevent_method_masking, _key_convert_hook =_key_convert_hook, _trackedIDs = trackedIDs)
                if type(v) is list:
                    l = []
                    for i in v:
                        n = i
                        if isinstance(i, dict):
                            idi = id(i)
                            if idi in trackedIDs:
                                n = trackedIDs[idi]
                            else:
                                trackedIDs[idi] = i
                                n = self.__class__(i, _dynamic=self._dynamic, _key_convert_hook =_key_convert_hook, _prevent_method_masking = self._prevent_method_masking)
                        l.append(n)
                    v = l
                self._map[k] = v
        if kwargs:
            for k,v in self.__call_items(kwargs):
                if self._prevent_method_masking and k in reserved_keys:
                    raise KeyError('"{}" is reserved'.format(k))
                if _key_convert_hook:
                    k = _key_convert_hook(k)
                self._map[k] = v

    def __call_items(self, obj):
        if hasattr(obj, 'iteritems') and ismethod(getattr(obj, 'iteritems')):
            return obj.iteritems()
        else:
            return obj.items()

    def items(self):
        return self.iteritems()

    def iteritems(self):
        return self.__call_items(self._map)

    def __iter__(self):
        return self._map.__iter__()

    def next(self):
        return self._map.next()

    def __setitem__(self, k, v):
        self._map[k] = v
    def __getitem__(self, k):
        if k not in self._map and self._dynamic and k != '_ipython_canary_method_should_not_exist_':
            # automatically extend to new DotMap
            self[k] = self.__class__()
        return self._map[k]

    def __setattr__(self, k, v):
        if k in {'_map','_dynamic', '_ipython_canary_method_should_not_exist_', '_prevent_method_masking'}:
            super(DotMap, self).__setattr__(k,v)
        elif self._prevent_method_masking and k in reserved_keys:
            raise KeyError('"{}" is reserved'.format(k))
        else:
            self[k] = v

    def __getattr__(self, k):
        if k.startswith('__') and k.endswith('__'):
            raise AttributeError(k)

        if k in {'_map','_dynamic','_ipython_canary_method_should_not_exist_'}:
            return super(DotMap, self).__getattr__(k)

        try:
            v = super(self.__class__, self).__getattribute__(k)
            return v
        except AttributeError:
            pass

        try:
            return self[k]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{k}'") from None

    def __delattr__(self, key):
        return self._map.__delitem__(key)

    def __contains__(self, k):
        return self._map.__contains__(k)

    def __add__(self, other):
        if self.empty():
            return other
        else:
            self_type = type(self).__name__
            other_type = type(other).__name__
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            raise TypeError(msg.format(self_type, other_type))

    def __str__(self, seen = None):
        items = []
        seen = {id(self)} if seen is None else seen
        for k,v in self.__call_items(self._map):
            # circular assignment case
            if isinstance(v, self.__class__):
                if id(v) in seen:
                    items.append('{0}={1}(...)'.format(k, self.__class__.__name__))
                else:
                    seen.add(id(v))
                    items.append('{0}={1}'.format(k, v.__str__(seen)))
            else:
                items.append('{0}={1}'.format(k, repr(v)))
        joined = ', '.join(items)
        out = '{0}({1})'.format(self.__class__.__name__, joined)
        return out

    def __repr__(self):
        return str(self)

    def toDict(self, seen = None):
        if seen is None:
            seen = {}

        d = {}

        seen[id(self)] = d

        for k,v in self.items():
            if issubclass(type(v), DotMap):
                idv = id(v)
                if idv in seen:
                    v = seen[idv]
                else:
                    v = v.toDict(seen = seen)
            elif type(v) in (list, tuple):
                l = []
                for i in v:
                    n = i
                    if issubclass(type(i), DotMap):
                        idv = id(n)
                        if idv in seen:
                            n = seen[idv]
                        else:
                            n = i.toDict(seen = seen)
                    l.append(n)
                if type(v) is tuple:
                    v = tuple(l)
                else:
                    v = l
            d[k] = v
        return d

    def pprint(self, pformat='dict'):
        if pformat == 'json':
            print(dumps(self.toDict(), indent=4, sort_keys=True))
        else:
            pprint(self.toDict())

    def empty(self):
        return (not any(self))

    # proper dict subclassing
    def values(self):
        return self._map.values()

    # ipython support
    def __dir__(self):
        return self.keys()

    @classmethod
    def parseOther(self, other):
        if issubclass(type(other), DotMap):
            return other._map
        else:
            return other
    def __cmp__(self, other):
        other = DotMap.parseOther(other)
        return self._map.__cmp__(other)
    def __eq__(self, other):
        other = DotMap.parseOther(other)
        if not isinstance(other, dict):
            return False
        return self._map.__eq__(other)
    def __ge__(self, other):
        other = DotMap.parseOther(other)
        return self._map.__ge__(other)
    def __gt__(self, other):
        other = DotMap.parseOther(other)
        return self._map.__gt__(other)
    def __le__(self, other):
        other = DotMap.parseOther(other)
        return self._map.__le__(other)
    def __lt__(self, other):
        other = DotMap.parseOther(other)
        return self._map.__lt__(other)
    def __ne__(self, other):
        other = DotMap.parseOther(other)
        return self._map.__ne__(other)

    def __delitem__(self, key):
        return self._map.__delitem__(key)
    def __len__(self):
        return self._map.__len__()
    def clear(self):
        self._map.clear()
    def copy(self):
        return self.__class__(self)
    def __copy__(self):
        return self.copy()
    def __deepcopy__(self, memo=None):
        return self.copy()
    def get(self, key, default=None):
        return self._map.get(key, default)
    def has_key(self, key):
        return key in self._map
    def iterkeys(self):
        return self._map.iterkeys()
    def itervalues(self):
        return self._map.itervalues()
    def keys(self):
        return self._map.keys()
    def pop(self, key, default=None):
        return self._map.pop(key, default)
    def popitem(self):
        return self._map.popitem()
    def setdefault(self, key, default=None):
        return self._map.setdefault(key, default)
    def update(self, *args, **kwargs):
        if len(args) != 0:
            self._map.update(*args)
        self._map.update(kwargs)
    def viewitems(self):
        return self._map.viewitems()
    def viewkeys(self):
        return self._map.viewkeys()
    def viewvalues(self):
        return self._map.viewvalues()
    @classmethod
    def fromkeys(cls, seq, value=None):
        d = cls()
        d._map = OrderedDict.fromkeys(seq, value)
        return d
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)
    # bannerStr
    def _getListStr(self,items):
        out = '['
        mid = ''
        for i in items:
            mid += '  {}\n'.format(i)
        if mid != '':
            mid = '\n' + mid
        out += mid
        out += ']'
        return out
    def _getValueStr(self,k,v):
        outV = v
        multiLine = len(str(v).split('\n')) > 1
        if multiLine:
            # push to next line
            outV = '\n' + v
        if type(v) is list:
            outV = self._getListStr(v)
        out = '{} {}'.format(k,outV)
        return out
    def _getSubMapDotList(self, pre, name, subMap):
        outList = []
        if pre == '':
            pre = name
        else:
            pre = '{}.{}'.format(pre,name)
        def stamp(pre,k,v):
            valStr = self._getValueStr(k,v)
            return '{}.{}'.format(pre, valStr)
        for k,v in subMap.items():
            if isinstance(v,DotMap) and v != DotMap():
                subList = self._getSubMapDotList(pre,k,v)
                outList.extend(subList)
            else:
                outList.append(stamp(pre,k,v))
        return outList
    def _getSubMapStr(self, name, subMap):
        outList = ['== {} =='.format(name)]
        for k,v in subMap.items():
            if isinstance(v, self.__class__) and v != self.__class__():
                # break down to dots
                subList = self._getSubMapDotList('',k,v)
                # add the divit
                # subList = ['> {}'.format(i) for i in subList]
                outList.extend(subList)
            else:
                out = self._getValueStr(k,v)
                # out = '> {}'.format(out)
                out = '{}'.format(out)
                outList.append(out)
        finalOut = '\n'.join(outList)
        return finalOut
    def bannerStr(self):
        lines = []
        previous = None
        for k,v in self.items():
            if previous == self.__class__.__name__:
                lines.append('-')
            out = ''
            if isinstance(v, self.__class__):
                name = k
                subMap = v
                out = self._getSubMapStr(name,subMap)
                lines.append(out)
                previous = self.__class__.__name__
            else:
                out = self._getValueStr(k,v)
                lines.append(out)
                previous = 'other'
        lines.append('--')
        s = '\n'.join(lines)
        return s

reserved_keys = {i for i in dir(DotMap) if not i.startswith('__') and not i.endswith('__')}
 