import os,win32file,win32api,win32con,uuid
def le3264run(game):
    b=win32file.GetBinaryType(game)
    if b==0: 
            #le=os.path.join(os.path.abspath(globalconfig['LocaleEmulator']),'LEProc.exe')
            le=os.path.join(os.path.abspath('./files/Locale.Emulator.2.5.0.1'),'LEProc.exe')
            if os.path.exists(le): 
                    if os.path.exists(game+'.le.config')==False:
                            writeleconfig(game)
                                
                    win32api.ShellExecute(None, "open", le, f'-run "{game}"', os.path.dirname(game), win32con.SW_SHOW)
    elif b==6: 
            #le=os.path.join(os.path.abspath(globalconfig['Locale_Remulator']),'LRProc.exe')
            le=os.path.join(os.path.abspath('./files/Locale_Remulator.1.5.0'),'LRProc.exe')
            if os.path.exists(le): 
                    #dll=os.path.join(os.path.abspath(globalconfig['Locale_Remulator']),'LRHookx64.dll')
                    #win32api.ShellExecute(None, "open", 'powershell', f'{le} {dll} 5f4c9504-8e76-46e3-921b-684d7826db71 "{ (game)}"', os.path.dirname(game), win32con.SW_HIDE)
                    win32api.ShellExecute(None, "open", le, f'5f4c9504-8e76-46e3-921b-684d7826db71 "{ (game)}"', os.path.dirname(game), win32con.SW_HIDE)


def writeleconfig(game):
         
        leconfig='''<?xml version="1.0" encoding="utf-8"?>
<LEConfig>
  <Profiles>
    <Profile Name="%s.le.config" Guid="%s" MainMenu="false">
      <Parameter></Parameter>
      <Location>ja-JP</Location>
      <Timezone>Tokyo Standard Time</Timezone>
      <RunAsAdmin>false</RunAsAdmin>
      <RedirectRegistry>true</RedirectRegistry>
      <IsAdvancedRedirection>false</IsAdvancedRedirection>
      <RunWithSuspend>false</RunWithSuspend>
    </Profile>
  </Profiles>
</LEConfig>
'''     
        with open(game+'.le.config','w',encoding='utf8') as ff :
                ff.write(leconfig %(os.path.basename(game),uuid.uuid1()))