import time
import win32pipe, win32file, pywintypes
import subprocess 
from threading import Thread
def recv():
    print("pipe recv")
    quit = False
 

    handle = win32pipe.CreateNamedPipe(
        # r'\\.\pipe\Foo',
        r'\\.\\Pipe\\textractorcommand',
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None)
    handle2 = win32pipe.CreateNamedPipe(
        # r'\\.\pipe\Foo',
        r'\\.\\Pipe\\textractoroutput',
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None) 
    win32pipe.ConnectNamedPipe(handle, None)
    win32pipe.ConnectNamedPipe(handle2,None)
    win32file.WriteFile(handle, bytes(f'attach -P28084',encoding='utf8') )

    while True:
        data = win32file.ReadFile(handle2, 65535, None)
        
        paste_str=str(data[1],encoding='utf8',  ) 
        print(paste_str) 
        # while True:
        #     time.sleep(1)
        #     a=input()
        #     win32file.WriteFile(handle, bytes(a,encoding='utf8') )      
     
    #p=subprocess.Popen(f"./Textractor/x64/TextractorCLI.exe",stdout=subprocess.PIPE)
    
    time.sleep(999999999)
    
    



if __name__ == '__main__':
    recv()