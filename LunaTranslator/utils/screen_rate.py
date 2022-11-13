 
import win32con,win32gui,win32print,win32api

def getScreenRate() :
    hDC = win32gui.GetDC(0) 
    screen_scale_rate = round(win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES) /  win32api.GetSystemMetrics(0), 2)


    return screen_scale_rate