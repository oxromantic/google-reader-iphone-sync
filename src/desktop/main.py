#!/opt/local/bin/python2.5
# to run (in vim)
# !`pwd`/%
import sys
import os
import urllib

import gtk
import gobject
import webkit

sys.path.insert(0, os.path.dirname(__file__) + '/../sync')
import db as database
import app_globals
gris_folder = os.path.expanduser("~/.GRiS/")
app_globals.OPTIONS['output_path'] = gris_folder
db = None

class Gris(object):
	def __init__(self):
		self.folders = ("images", "text", "foo")
		self.init_ui()

	def on_window_destroy(self, widget, data=None):
		gtk.main_quit()
	
	def init_ui(self):
		builder = gtk.Builder()
		builder.add_from_file("main.glade")

		def set_object(name):
			setattr(self, name, builder.get_object(name))
			
		map(set_object, ("window", "feed_tree_view", "content_scroll_view"))
		builder.connect_signals(self)
		self.init_feeds()
		self.init_columns()
		self.init_content()

	def on_feed_tree_view_select_row(self, widget, data=None):
		base = 'file://' + urllib.quote(gris_folder)
		selected = []
		content_col = 2
		title_col = 0
		store, iter = self.feed_tree_view.get_selection().get_selected()
		content = store.get_value(iter, content_col)
		title = store.get_value(iter, title_col)
		self.content_view.load_html_string("""
			<h1>%s</h1>
			%s
			""" % (title, content), base)

	def init_content(self):
		self.content_view = webkit.WebView()
		self.content_scroll_view.add(self.content_view)
		self.content_scroll_view.show_all()

	def init_feeds(self):
		store = self.feed_tree_store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING)
		cursor = db.sql("select title, content from items")
		print repr(cursor)
		for feed_name, content in cursor:
			store.set(store.append(None), 0, feed_name, 1, 100, 2, content)
		self.feed_tree_view.set_model(store)
	
	def init_columns(self):
		view = self.feed_tree_view
		view.append_column(gtk.TreeViewColumn('title', gtk.CellRendererText(), text=0))
		view.append_column(gtk.TreeViewColumn('items', gtk.CellRendererText(), text=1))

if __name__ == "__main__":
	db = database.DB(gris_folder + 'items.sqlite')
	gris = Gris()
	gris.window.show()
	gtk.main()

