

function NWjshook(){
    function NWjssend(s) {
        const _clipboard = require('nw.gui').Clipboard.get();
        _clipboard.set(s, 'text'); 
        return _clipboard.get('text')
    }
    
    Window_Message.prototype.originstartMessage=Window_Message.prototype.startMessage;
    Window_Message.prototype.startMessage = function() 
    {
        gametext = $gameMessage.allText();
        resp=NWjssend(gametext);
        $gameMessage._texts=[resp]
        this.originstartMessage();
    };
}

function Electronhook() {
        
    function Electronsend(s) {
        const { clipboard } = require('electron');
        clipboard.writeText(s);
        return clipboard.readText();
    }
    const _text_showMessage = tyrano.plugin.kag.tag.text.showMessage;
    tyrano.plugin.kag.tag.text.showMessage = function () {
        arguments[0]=Electronsend(arguments[0]);
        return _text_showMessage.apply(this, arguments);
    }
    
}

setTimeout(()=>{
    if(window.tyrano && tyrano.plugin){
        Electronhook();
    }
    else if(window.Utils && Utils.RPGMAKER_NAME){
        NWjshook();
    }
},5000);
