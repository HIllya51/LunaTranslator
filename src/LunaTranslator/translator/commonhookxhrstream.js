(function () {
    window.hasdone = false
    window.thistext = ''
    if (window.injectedjs) return
    window.injectedjs = true
    const originXHR = XMLHttpRequest
    window.XMLHttpRequest = function () {
        var newxhr = new originXHR()
        newxhr.open_ori = newxhr.open

        newxhr.open = function () {
            var url = arguments[1]
            if (% s) {
                window.hasdone = false;
                window.thistext = ''
                newxhr.onprogress_ori = newxhr.onprogress
                newxhr.onload_ori = newxhr.onload_ori
                newxhr.offset = 0
                newxhr.onload = function () {
                    hasdone = true;
                    if (newxhr.onload_ori)
                        return newxhr.onload_ori.apply(this, arguments);
                };
                newxhr.onprogress = function (event) {
                    var current = newxhr.responseText
                    var lines = current.substring(newxhr.offset)
                    lines = lines.split('\n')
                    for (let i = 0; i < lines.length; i++) {
                        let line = lines[i]
                        line = line.trim()
                        if (line.length == 0) continue;
                        if (line.substring(6) == '[DONE]') {
                            hasdone = true;
                            break;
                        }
                        try {
                            const chunk = JSON.parse(line.substring(6));
                                % s
                        } catch {

                        }
                    }
                    newxhr.offset = current.length;
                    if (newxhr.onprogress_ori)
                        return newxhr.onprogress_ori.apply(this, arguments);
                };
            }
            return newxhr.open_ori.apply(this, arguments);
        };

        return newxhr
    }
})()