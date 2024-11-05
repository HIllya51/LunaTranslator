var fontface = '';
var magicsend = '\x01LUNAFROMJS\x01'
var magicrecv = '\x01LUNAFROMHOST\x01'
var is_packed = IS_PACKED
var is_useclipboard = IS_USECLIPBOARD
var internal_http_port = INTERNAL_HTTP_PORT
function splitfonttext(transwithfont) {
    if (transwithfont.substr(0, magicsend.length) == magicsend) //not trans
    {
        split = transwithfont.search('\x02')
        return transwithfont.substr(split + 1);
    }
    else if (transwithfont.substr(0, magicrecv.length) == magicrecv) {
        transwithfont = transwithfont.substr(magicrecv.length)
        split = transwithfont.search('\x02')
        fontface = transwithfont.substr(0, split)
        text = transwithfont.substr(split + 1)
        return text;
    }
    else {
        return transwithfont;
    }
}
function cppjsio(name, s_raw, lpsplit, embedable) {
    if (!s_raw)
        return s_raw
    transwithfont = ''
    s = magicsend + name + '\x03' + lpsplit.toString() + '\x04' + (embedable ? '1' : '0') + '\x02' + s_raw;
    if (internal_http_port) {
        var xhr = new XMLHttpRequest();
        var url = 'http://127.0.0.1:' + internal_http_port + '/fuck'
        xhr.open('POST', url, false);
        xhr.send(s);
        if (xhr.status === 200) {
            transwithfont = xhr.responseText;
        }
    }
    else if (is_useclipboard) {
        try {
            const _clipboard = require('nw.gui').Clipboard.get();
            _clipboard.set(s, 'text');
            transwithfont = _clipboard.get('text');
        }
        catch (err) {
            try {
                const clipboard = require('electron').clipboard;
                clipboard.writeText(s);
                transwithfont = clipboard.readText();
            }
            catch (err2) {
            }
        }
    }
    if (!transwithfont) return s_raw;
    return splitfonttext(transwithfont)
}

function rpgmakerhook() {

    if (Window_Message.prototype.originstartMessage) { }
    else {
        Window_Base.prototype.drawTextEx_origin = Window_Base.prototype.drawTextEx;
        Window_Base.prototype.drawText_origin = Window_Base.prototype.drawText;
        Window_Message.prototype.originstartMessage = Window_Message.prototype.startMessage;
        Window_Message.prototype.updateMessage_ori = Window_Message.prototype.updateMessage;

        Bitmap.prototype.drawText_ori = Bitmap.prototype.drawText;
        Bitmap.prototype.last_y = 0;

        Bitmap.prototype.origin_makeFontNameText = Bitmap.prototype._makeFontNameText;
    }
    Bitmap.prototype._makeFontNameText = function () {
        if (!fontface) return this.origin_makeFontNameText();
        return (this.fontItalic ? 'Italic ' : '') +
            this.fontSize + 'px ' + fontface;
    }
    Bitmap.prototype.collectstring = { 2: '', 5: '', 6: '' };
    setInterval(function () {
        for (lpsplit in Bitmap.prototype.collectstring) {
            if (Bitmap.prototype.collectstring[lpsplit].length) {
                cppjsio('rpgmakermv', Bitmap.prototype.collectstring[lpsplit], lpsplit, false)
                Bitmap.prototype.collectstring[lpsplit] = ''
            }
        }
    }, 100);
    if (!is_packed) {

        Bitmap.prototype.drawText = function (text, x, y, maxWidth, lineHeight, align) {
            //y>100的有重复；慢速是单字符，快速是多字符
            if (text && (y < 100)) {
                extra = 5 + ((text.length == 1) ? 0 : 1);
                if (y != Bitmap.prototype.last_y) {
                    Bitmap.prototype.collectstring[extra] += '\n'
                }
                Bitmap.prototype.collectstring[extra] += text;
                Bitmap.prototype.last_y = y;
            }
            return this.drawText_ori(text, x, y, maxWidth, lineHeight, align);
        }
    }
    Window_Message.prototype.startMessage = function () {
        gametext = $gameMessage.allText();
        resp = cppjsio('rpgmakermv', gametext, 0, true);
        $gameMessage._texts = [resp]
        this.originstartMessage();
    };
    Window_Message.prototype.lastalltext = ''
    Window_Message.prototype.updateMessage = function () {
        if (this._textState) {
            if (Window_Message.prototype.lastalltext != $gameMessage.allText()) {
                cppjsio('rpgmakermv', $gameMessage.allText(), 18, false);
                Window_Message.prototype.lastalltext = $gameMessage.allText()
            }
        }
        return this.updateMessage_ori();
    };
    Window_Base.prototype.drawText = function (text, x, y, maxWidth, align) {
        text = cppjsio('rpgmakermv', text, 1, true)
        return this.drawText_origin(text, x, y, maxWidth, align)
    }
    Window_Base.prototype.lastcalltime = 0
    Window_Base.prototype.drawTextEx = function (text, x, y) {
        __last = Window_Base.prototype.lastcalltime
        __now = new Date().getTime()
        Window_Base.prototype.lastcalltime = __now
        if (__now - __last > 100)
            text = cppjsio('rpgmakermv', text, 2, true)
        else {
            Bitmap.prototype.collectstring[2] += text;
        }
        return this.drawTextEx_origin(text, x, y)
    }
}

function tyranohook() {

    if (tyrano.plugin.kag.tag.text.originstart) return;
    tyrano.plugin.kag.tag.text.originstart = tyrano.plugin.kag.tag.text.start;
    tyrano.plugin.kag.tag.chara_ptext.startorigin = tyrano.plugin.kag.tag.chara_ptext.start;
    tyrano.plugin.kag.tag.text.start = function (pm) {
        if (1 != this.kag.stat.is_script && 1 != this.kag.stat.is_html) {
            pm.val = cppjsio('tyranoscript', pm.val, 0, true);
            if (fontface) {
                this.kag.stat.font.face = fontface
            }
        }
        return this.originstart(pm)
    }
    tyrano.plugin.kag.tag.chara_ptext.start = function (pm) {
        pm.name = cppjsio('tyranoscript', pm.name, 1, true)
        return this.startorigin(pm)
    }
}
function retryinject(times) {
    if (times == 0) return;
    try {
        if (window.tyrano && tyrano.plugin) {
            tyranohook();
        }
        else if (window.Utils && Utils.RPGMAKER_NAME) {
            rpgmakerhook();
        }
        else {
            setTimeout(retryinject, 3000, times - 1);
        }
    }
    catch (err) {
        //非主线程，甚至没有window对象，会弹窗报错
    }
}
retryinject(3)