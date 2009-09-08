#!/opt/local/bin/python2.5
# to run (in vim)
# !`pwd`/%
import sys
import os
import urllib

import gtk
import gobject
import webkit

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
		_dir = os.path.dirname(os.path.abspath(__file__))
		base = 'file://' + urllib.quote(_dir)
		selected = []
		col = 0
		store, iter = self.feed_tree_view.get_selection().get_selected()
		feed_name = store.get_value(iter, col)
		self.content_view.load_html_string("<h1>yay!</h1><pre>loaded: %r</pre>" % (feed_name,), base)

	def init_content(self):
		self.content_view = webkit.WebView()
		self.content_scroll_view.add(self.content_view)
		self.content_scroll_view.show_all()

	def init_feeds(self):
		store = self.feed_tree_store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
		store.set(store.append(None), 0, "all feeds", 1, 500)
		store.set(store.append(None), 0, "more feeds", 1, 200)
		self.feed_tree_view.set_model(store)
	
	def init_columns(self):
		view = self.feed_tree_view
		view.append_column(gtk.TreeViewColumn('title', gtk.CellRendererText(), text=0))
		view.append_column(gtk.TreeViewColumn('items', gtk.CellRendererText(), text=1))

if __name__ == "__main__":
	gris = Gris()
	gris.window.show()
	gtk.main()

