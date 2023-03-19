class ObjectPrototype:
    def toString():
        return '[object %s]' % this.Class

    def valueOf():
        return this.to_object()

    def toLocaleString():
        return this.callprop('toString')

    def hasOwnProperty(prop):
        return this.get_own_property(prop.to_string().value) is not None

    def isPrototypeOf(obj):
        #a bit stupid specification but well
        # for example Object.prototype.isPrototypeOf.call((5).__proto__, 5) gives false
        if not obj.is_object():
            return False
        while 1:
            obj = obj.prototype
            if obj is None or obj.is_null():
                return False
            if obj is this:
                return True

    def propertyIsEnumerable(prop):
        cand = this.own.get(prop.to_string().value)
        return cand is not None and cand.get('enumerable')
