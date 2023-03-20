import os,win32utils
def le3264run(game,alwaysuselr): 
    try:
        b=win32utils.GetBinaryType(game)
        if b==0 and alwaysuselr==False: 
            #le=os.path.join(os.path.abspath(globalconfig['LocaleEmulator']),'LEProc.exe')
            le=os.path.join(os.path.abspath('./files/plugins/Locale.Emulator'),'cleproc.exe')
            if os.path.exists(le): 
                    win32utils.CreateProcess(None,f'"{le}" "{(game)}"', None,None,False,0,None, os.path.dirname(game), win32utils.STARTUPINFO()  ) 
        elif b==6 or alwaysuselr==True: 
                #le=os.path.join(os.path.abspath(globalconfig['Locale_Remulator']),'LRProc.exe')
                le=os.path.join(os.path.abspath('./files/plugins/Locale_Remulator'),'LRProc.exe')
                if os.path.exists(le):
                      win32utils.CreateProcess(None,f'"{le}" 5f4c9504-8e76-46e3-921b-684d7826db71 "{(game)}"', None,None,False,0,None, os.path.dirname(game), win32utils.STARTUPINFO()  ) 

    except:
        win32utils.CreateProcess(game,None, None,None,False,0,None, os.path.dirname(game), win32utils.STARTUPINFO()  ) 
    
