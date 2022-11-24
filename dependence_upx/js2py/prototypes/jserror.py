class ErrorPrototype:
    def toString():
        if this.TYPE != 'Object':
            raise this.MakeError(
                'TypeError', 'Error.prototype.toString called on non-object')
        name = this.get('name')
        name = 'Error' if name.is_undefined() else name.to_string().value
        msg = this.get('message')
        msg = '' if msg.is_undefined() else msg.to_string().value
        return name + (name and msg and ': ') + msg
