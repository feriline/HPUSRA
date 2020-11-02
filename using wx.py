
import wx
from win32gui import GetWindowText, GetForegroundWindow
from time import sleep, strftime, localtime
from ctypes import windll, Structure, c_uint, sizeof, byref

class TaskBarApp(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title, size = (1, 1), style=wx. FRAME_NO_TASKBAR |wx.NO_FULL_REPAINT_ON_RESIZE)
        self.ICON_STATE = 1
        self. ID_ICON_TIMER =wx.NewId()
        self.tbicon = wx.TaskBarIcon()
        icon = wx.Icon('logon.ico', wx.BITMAP_TYPE_ICO)
        self.tbicon.SetIcon(icon, 'Logging')
        self.tbicon.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.tbicon.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRightClick)
        self.Bind(wx.EVT_TIMER, self.Log, id=self.ID_ICON_TIMER)
        self.SetIconTimer()
        self.Show(True)
        self.lastInputInfo = self.LASTINPUTINFO()
        self.lastInputInfo.cbSize = sizeof(self.lastInputInfo)
        self.Write(self.Now( ) +"<|>__LOGGERSTART__<|>0\n")

    def OnTaskBarLeftDClick(self, evt):
        if self.ICON_STATE == 0:
            self.Write(self.Now( ) +"<|>__LOGGERUNPAUSE__<|>0\n")
            self.StartIconTimer()
            icon = wx.Icon('logon.ico', wx.BITMAP_TYPE_ICO)
            self.tbicon.SetIcon(icon, 'Logging')
            self.ICON_STATE = 1
        else:
            self.StopIconTimer()
            self.Write(self.Now( ) +"<|>__LOGGERPAUSE__<|>0\n")
            icon = wx.Icon('logoff.ico', wx.BITMAP_TYPE_ICO)
            self.tbicon.SetIcon(icon, 'Not Logging')
            self.ICON_STATE = 0

    def OnTaskBarRightClick(self, evt):
        self.StopIconTimer()
        self.Write(self.Now( ) +"<|>__LOGGERSTOP__<|>0\n")
        self.tbicon.Destroy()
        self.Close(True)
        wx.GetApp().ProcessIdle()

    def SetIconTimer(self):
        self.icontimer = wx.Timer(self, self.ID_ICON_TIMER)
        self.icontimer.Start(10000)

    def StartIconTimer(self):
        try:
            self.icontimer.Start(10000)
        except:
            pass

    def StopIconTimer(self):
        try:
            self.icontimer.Stop()
        except:
            pass

    def Log(self, evt):
        windll.user32.GetLastInputInfo(byref(self.lastInputInfo))
        idleDelta = float(windll.kernel32.GetTickCount() - self.lastInputInfo.dwTime) / 1000
        self.Write(self.Now( ) + "<|>" +GetWindowText(GetForegroundWindow() ) + "<|>" +str(idleDelta ) +"\n")

    def Write(self, text):
        f=open( 'log.tmp', 'a')
        f.write (text)
        f.close()
    def Now(self):
        return strftime("%Y-%m-%d %H:%M:%S", localtime())

    class LASTINPUTINFO(Structure):
        _fields_ = [("cbSize", c_uint),( "dwTime", c_uint)]


class MyApp(wx.App):
    def OnInit(self):
        frame = TaskBarApp(None, -1, ' ')
        frame.Center(wx.BOTH)
        frame.Show(False)
        return True

def main():
    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    main()

