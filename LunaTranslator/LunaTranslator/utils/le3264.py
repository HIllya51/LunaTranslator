import os,win32utils,win32con,uuid
def le3264run(game,alwaysuselr): 
    try:
        b=win32utils.GetBinaryType(game)
        if b==0 and alwaysuselr==False: 
            #le=os.path.join(os.path.abspath(globalconfig['LocaleEmulator']),'LEProc.exe')
            le=os.path.join(os.path.abspath('./files/plugins/Locale.Emulator'),'cleproc.exe')
            if os.path.exists(le): 
                    win32utils.ShellExecute(None, "open", le, f'"{game}"', os.path.abspath('./files/plugins/Locale.Emulator'), win32con.SW_SHOW)
        elif b==6 or alwaysuselr==True: 
                #le=os.path.join(os.path.abspath(globalconfig['Locale_Remulator']),'LRProc.exe')
                le=os.path.join(os.path.abspath('./files/plugins/Locale_Remulator'),'LRProc.exe')
                if os.path.exists(le): 
                        
                      win32utils.ShellExecute(None, "open", le, f'5f4c9504-8e76-46e3-921b-684d7826db71 "{ (game)}"', os.path.dirname(game), win32con.SW_HIDE)

    except:
        win32utils.ShellExecute(None, "open", game, '', os.path.dirname(game), win32con.SW_SHOW) 
    
