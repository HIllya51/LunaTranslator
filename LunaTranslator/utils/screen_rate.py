 
from win32.win32api import GetSystemMetrics  
import win32con,win32gui,win32print

def getScreenRate() :
    hDC = win32gui.GetDC(0) 
    screen_scale_rate = round(win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES) /  GetSystemMetrics(0), 2)


    return screen_scale_rate