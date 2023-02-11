import subprocess,time

import win32pipe, win32file,win32con,win32event,win32security
attr=win32security.SECURITY_DESCRIPTOR(win32con.SECURITY_DESCRIPTOR_REVISION)
attr.SetSecurityDescriptorDacl(True,None,False) 
secu=win32security.SECURITY_ATTRIBUTES() 
secu.SECURITY_DESCRIPTOR=attr
secu.bInheritHandle=False 
  
t=time.time()
t= str(t) 
import mmap

print(f'C:/Users/11737/Documents/GitHub/LunaTranslator/CXXplugins/win32dllforward/Release/jbj7_3.exe C:/dataH/JBeijing7/JBJCT.dll {"jbj7_sentence_"+t} {"jbj7_trans_"+t} {"jbj7_code_"+t} {"jbj7_waitsentence_"+t} {"jbj7_waittrans_"+t} {"jbj7_waitdllload_"+t}') 

x=subprocess.Popen(f'C:/Users/11737/Documents/GitHub/LunaTranslator/CXXplugins/win32dllforward/Release/jbj7_3.exe C:/dataH/JBeijing7/JBJCT.dll {"jbj7_sentence_"+t} {"jbj7_trans_"+t} {"jbj7_code_"+t} {"jbj7_waitsentence_"+t} {"jbj7_waittrans_"+t} {"jbj7_waitdllload_"+t}') 
win32event.WaitForSingleObject(win32event.CreateEvent(secu,False, False,  "jbj7_waitdllload_"+t),win32event.INFINITE);
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
waitforjp=win32event.CreateEvent(secu,False, False,  "jbj7_waitsentence_"+t)
notifyfortranslateover=win32event.CreateEvent(secu,False, False,  "jbj7_waittrans_"+t)  
 
fr = mmap.mmap(0, 6000, "jbj7_sentence_"+t,mmap.ACCESS_WRITE)
to = mmap.mmap(0, 6000, "jbj7_trans_"+t, mmap.ACCESS_WRITE)
wcode = mmap.mmap(0, 20, "jbj7_code_"+t, mmap.ACCESS_WRITE)
fr.write('おはよう\0'.encode('utf-16-le'))
wcode.write('936\0'.encode('utf-16-le')) 
win32event.SetEvent(waitforjp)  
win32event.WaitForSingleObject(notifyfortranslateover,win32event.INFINITE);
print(to.read().decode('utf-16-le'))  

fr.seek(0)
wcode.seek(0)
to.seek(0)
fr.write('おはよう111\0'.encode('utf-16-le'))
wcode.write('936\0'.encode('utf-16-le')) 
win32event.SetEvent(waitforjp)  
win32event.WaitForSingleObject(notifyfortranslateover,win32event.INFINITE);
print(to.read().decode('utf-16-le'))  
x.kill()