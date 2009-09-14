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
		content = store.get_value(iter, FeedTreeModel.COL_NAME)
		title = store.get_value(iter, FeedTreeModel.COL_NAME)
		self.content_view.load_html_string("""
			<h1>%s</h1>
			%s
			""" % (title, content), base)

	def init_content(self):
		self.content_view = webkit.WebView()
		self.content_scroll_view.add(self.content_view)
		self.content_scroll_view.show_all()

	def init_feeds(self):
		self.feed_tree_store = FeedTreeModel(db)
		self.feed_tree_view.set_model(self.feed_tree_store)
	
	def init_columns(self):
		self.feed_tree_store.populate_view_columns(self.feed_tree_view)


class FeedTreeModel(gtk.GenericTreeModel):
	TYPE_TAG = 0
	TYPE_FEED = 1
	TYPE_ENTRY = 2

	COL_TYPE = 0
	COL_ID = 1
	COL_NAME = 2
	COL_COUNT = 3

	def __init__(self, db):
		self.db = db
		self.columns = (
			('type', gobject.TYPE_INT),
			('id', gobject.TYPE_STRING),
			('name', gobject.TYPE_STRING),
			('count', gobject.TYPE_INT),
		)
		tag_rows = []
		self.root = [None, None, None, None, tag_rows]
		tags = self.db.get_tags_and_counts()

		tag_rows.append(self._row_of_type(
				type(self).TYPE_TAG,
				{'id':None, 'name':'[All Items]', 'count':self.db.get_item_count()}))

		for tag in tags:
			tag_rows.append(self._row_of_type(
				type(self).TYPE_TAG,
				tag))
		super(type(self), self).__init__()
	
	def populate_view_columns(self, view):
		view.append_column(gtk.TreeViewColumn('title', gtk.CellRendererText(), text=type(self).COL_NAME))
		view.append_column(gtk.TreeViewColumn('items', gtk.CellRendererText(), text=type(self).COL_COUNT))
		view.set_expander_column(view.get_column(0))
		# view.expand_all()
	
	def _row_of_type(self, type, dict_):
		return [type, dict_['id'], dict_['name'], dict_['count'], None]

	def _children_for_tag(self, tag):
		data = []
		for feed in self.db.get_feeds_and_counts(tag_name=tag):
			data.append(self._row_of_type(self.TYPE_FEED, feed))
		return data

	def _children_for_feed(self, feed_id):
		data = []
		for entry in self.db.get_item_list_for_feed(feed_id=feed_id):
			data.append(self._row_of_type(self.TYPE_ENTRY, entry))
		return data

	def _children_for_row_with_depth(self, row, depth):
		logging.debug("loading children at depth=%s, row=%r" % (depth, row))
		if depth == self.TYPE_FEED:
			return self._children_for_tag(row[self.COL_NAME])
		elif depth == self.TYPE_ENTRY:
			return self._children_for_feed(row[self.COL_ID])
		else:
			raise RuntimeError("invalid depth requested: %s" % (depth,))
	
	def _lookup(self, path, populate_leaf=False):
		#logging.debug("looking up path: %r" % (path,))
		if path is None: path = []
		result = self.root
		depth = 0
		def fill(row, depth):
			if row[-1] is None:
				row[-1] = self._children_for_row_with_depth(row, depth)
			
		for index in path:
			fill(result, depth)
			depth += 1
			result = result[-1][index]

		if populate_leaf:
			fill(result, depth)
		return result

	def on_get_flags(self):
		return 0

	def on_get_n_columns(self):
		return len(self.columns)

	def on_get_column_type(self, index):
		return self.columns[index][1]

	def on_get_iter(self, path):
		return path

	def on_get_path(self, rowref):
		return rowref

	def on_get_value(self, rowref, column):
		return self._lookup(rowref)[column]

	def _copy_path(self, path):
		if path is None:
			return []
		return list(path)[:]

	def on_iter_next(self, rowref):
		items = self._lookup(rowref[:-1])[-1]
		new_leaf_ref = rowref[-1] + 1
		logging.debug("len(items) = %s, new_leaf_ref = %s" % (len(items), new_leaf_ref))
		if len(items) > new_leaf_ref:
			newref = self._copy_path(rowref)
			newref[-1] = new_leaf_ref
			logging.debug("iter next: returning %r" % (newref,))
			return newref
		return None

	def on_iter_children(self, parent_iter):
		return self.on_iter_nth_child(parent_iter, 0)
	
	def on_iter_has_child(self, rowref):
		logging.debug("has_children for rowref %r = %s" % (rowref, len(self._lookup(rowref, populate_leaf=True)[-1])))
		return len(self._lookup(rowref, populate_leaf=True)[-1]) > 0

	def on_iter_n_children(self, rowref):
		logging.debug("n_children for rowref %r = %s" % (rowref, len(self._lookup(rowref)[-1])))
		return len(self._lookup(rowref, populate_leaf=True)[-1])

	def on_iter_nth_child(self, parent, n):
		iter = self._copy_path(parent)
		if self.on_iter_n_children(parent) > n:
			iter.append(n)
			return iter

	def on_iter_parent(self, child):
		return list(child)[:-1]


if __name__ == "__main__":
	db = database.DB(gris_folder + 'items.sqlite')
	gris = Gris()
	gris.window.show()
	gtk.main()

