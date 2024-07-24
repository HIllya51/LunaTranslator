const originXHR = XMLHttpRequest

window.XMLHttpRequest = function () {
    var newxhr = new originXHR()
    newxhr.open_ori = newxhr.open

    newxhr.open = function () {
        var input=arguments[1]
        if (%s) {

            newxhr.onprogress_ori = newxhr.onprogress
            newxhr.offset=0
            newxhr.onprogress = function (event) {
                var current=newxhr.responseText
                var lines=current.substring(newxhr.offset)
                lines = lines.split('\n')
                for (let i = 0; i < lines.length; i++) {
                    let line = lines[i]
                    line = line.trim()
                    if (line.length == 0) continue;
                    try {
                        %s
                    } catch {

                    }
                }
                newxhr.offset=current.length;
                if(newxhr.onprogress_ori)
                    return newxhr.onprogress_ori.apply(this, arguments);
            };
        }
        return newxhr.open_ori.apply(this, arguments);
    };

    return newxhr
}