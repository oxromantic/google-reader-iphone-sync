#!/usr/bin/env python

#FIXME: linux version requires this before wx package is importable
import wxversion; wxversion.select(wxversion.getInstalled()[0])

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
		
		splitter.SetMinimumPaneSize(20)
		splitter.SplitVertically(self.feed_list, self.item_view, -100)

		
		# box = wx.BoxSizer(wx.HORIZONTAL)
		# box.Add(self.item_view, 0, wx.EXPAND)
		# box.Add(self.feed_list, 1, wx.EXPAND)
		# 	
		# panel.SetSizer(box)
		panel.Layout()

	def on_close(self, event):
		print "closed!"
		self.Destroy()
	
	def init_html(self, parent):
		wx.InitAllImageHandlers()
		item_view = wx.html.HtmlWindow(parent, -1)
		item_view.LoadPage("http://localhost:80/")
		return item_view
	
	def init_list(self, parent):
		feed_list = wx.TreeCtrl(parent, -1)
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
