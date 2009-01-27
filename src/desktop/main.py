import wx
import wx.html

import sys

from feeditem import FeedItem

sys.path.append('..')
from sync import main as sync_main
from sync.main import app_globals

global db

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title='GRiS')
		self.Bind(wx.EVT_CLOSE, self.on_close)

		panel = wx.Panel(self)
	
		splitter = wx.SplitterWindow(self, -1, style = wx.SP_LIVE_UPDATE)
		self.item_view = self.init_html(splitter)
		self.feed_list = self.init_list(splitter)
		
		splitter.SetMinimumPaneSize(80)
		splitter.SplitVertically(self.feed_list, self.item_view)
		splitter.SetSashPosition(200)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(splitter,1,wx.EXPAND)

		# layout
		self.SetSizer(sizer)
		self.SetAutoLayout(1)
		sizer.Fit(self)

		self.Show(True)

	def on_close(self, event):
		print "closed!"
		self.Destroy()
	
	def init_html(self, parent):
		wx.InitAllImageHandlers()
		item_view = wx.html.HtmlWindow(parent, -1)
		item_view.SetPage("<b>HI!</b>")

		# item_view = wx.Window(parent, style=wx.BORDER_SUNKEN)
		# item_view.SetBackgroundColour("sky blue")
		# wx.StaticText(item_view, -1, "This is an example of static text", (20, 10))

		return item_view
	
	def init_list(self, parent):
		feed_list = wx.Window(parent, style=wx.BORDER_SUNKEN)
		wx.TreeCtrl(feed_list, -1)
		return feed_list
	# 
	# def OnShow(self, evt):
	# 	print "showing..."
	# 	if self._shown:
	# 		return
	# 	else:
	# 		print "loading!"
	# 		self._shown = True
	# 		self.item_view.SetPage("http://localhost:80/")

def run_wx():
	app = wx.PySimpleApp()
	frame = MainFrame()
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
