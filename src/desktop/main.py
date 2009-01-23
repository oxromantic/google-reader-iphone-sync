import wx
import sys

sys.path.append('..')
from sync import main as sync_main
from sync.main import app_globals

global db

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title='GRiS')
		self.Bind(wx.EVT_CLOSE, self.on_close)

		panel = wx.Panel(self)
		box = wx.BoxSizer(wx.HORIZONTAL)
	
		self.item_view = self.init_html()
		self.feed_list = self.init_list()
		
		m_text = wx.StaticText(panel, -1, "Hello World!")
		m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text.SetSize(m_text.GetBestSize())

		box.Add(m_text, 0, wx.ALL, 2)
		box.Add(m_text, 1, wx.ALL, 2)
	
		panel.SetSizer(box)
		panel.Layout()

	def on_close(self, event):
		print "closed!"
		self.Destroy()
	
	def init_html(self):
		wx.InitAllImageHandlers()
		item_view = wx.html.HtmlWindow()
		return item_view
	
	def init_list(self):
		feed_list = wx.TreeCtrl()
		return feed_list
	

def run_wx():
	app = wx.PySimpleApp()
	frame = MainFrame()
	frame.Show()
	app.MainLoop()
	print "exiting..."
	sync_main.cleanup()

def main():
	global db
	sync_main.setup(['--output-path=~/.GRiS'])
	db = app_globals.DATABASE = sync_main.DB()
	items = db.get_items()
	run_wx()

if __name__ == '__main__':
	main()
