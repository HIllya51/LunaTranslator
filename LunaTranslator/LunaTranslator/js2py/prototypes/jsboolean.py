class BooleanPrototype:
    def toString():
        if this.Class != 'Boolean':
            raise this.Js(TypeError)('this must be a boolean')
        return 'true' if this.value else 'false'

    def valueOf():
        if this.Class != 'Boolean':
            raise this.Js(TypeError)('this must be a boolean')
        return this.value
