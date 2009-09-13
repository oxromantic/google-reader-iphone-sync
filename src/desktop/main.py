#!/opt/local/bin/python2.5
# to run (in vim)
# !`pwd`/%
import sys
import os
import urllib

import gtk
import gtk.keysyms
import gobject
import webkit

import logging
logging.basicConfig(level=logging.DEBUG)

import database
gris_folder = os.path.expanduser("~/.GRiS/")
db = None

class Object(object):
	def __init__(self, **kw):
		for k,v in kw.items():
			setattr(self,k,v)

class Gris(object):
	def __init__(self):
		self.folders = ("images", "text", "foo")
		self.init_ui()

	def on_window_destroy(self, widget, data=None):
		gtk.main_quit()

	def on_key_press(self, widget, event):
		actions = {
			gtk.keysyms.Escape: self.window.destroy,
		}
		try:
			actions[event.keyval]()
		except KeyError:
			pass
	
	def init_ui(self):
		builder = gtk.Builder()
		builder.add_from_file("main.glade")

		def set_object(name):
			setattr(self, name, builder.get_object(name))
			
		map(set_object, ("window", "feed_tree_view", "content_scroll_view"))
		builder.connect_signals(self)
		self.init_actions()
		self.init_feeds()
		self.init_columns()
		self.init_content()

	def init_actions(self):
		accel_grp = gtk.AccelGroup()
		exit = gtk.Action("gris.exit", "Exit", None, None)
		exit.set_accel_group(accel_grp)
		exit.set_accel_path("app.exit")
		exit.connect("activate",  lambda widget, obj: self.on_window_destroy())
		gtk.accel_map_add_entry("app.exit", gtk.keysyms.Escape, 0)
		self.window.add_accel_group(accel_grp)

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
		store.set(store.append(None), 0, "All feeds", 1, db.get_item_count())
		for tag in db.get_tags_and_counts():
			store.set(store.append(None), 0, tag['name'], 1, tag['count'])
			
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

