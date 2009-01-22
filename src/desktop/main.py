import wx

app = wx.PySimpleApp()
frame = wx.Frame(None, wx.ID_ANY, "Hello World")
frame.Show(True)

if __name__ == '__main__':
	app.MainLoop()
	