import glob
import os
import sqlite3 as sqlite


import logging
debug = logging.debug

class DB(object):
	def __init__(self, filename = 'items.sqlite'):
		self.filename = filename
		debug("loading db: %s" % filename)
		self.db = sqlite.connect(filename)

		self.schema = {
			'columns': [
				('google_id','TEXT primary key'),
				('date', 'TIMESTAMP'),
				('url', 'TEXT'),
				('original_id', 'TEXT'),
				('title', 'TEXT'),
				('content', 'TEXT'),
				('feed_name', 'TEXT'),
				('is_read', 'BOOLEAN'),
				('is_starred', 'BOOLEAN'),
				('is_dirty', 'BOOLEAN default 0'),
				('had_errors', 'BOOLEAN default 0'),
				('is_stale', 'BOOLEAN default 0'),
				('tag_name', 'TEXT'),
				('is_shared', 'BOOLEAN'),
				('instapaper_url', 'TEXT'),
				('is_pagefeed', 'BOOLEAN'),
				('feed_id','TEXT'),
			],
			'indexes' : [ ('item_id_index', 'items(google_id)') ]
		}
		self.cols = [x for (x,y) in self.schema['columns']]

	def sql(self, stmt, data = None):
		args = [stmt]
		if data is not None:
			args.append(data)

		return self.db.execute(*args)
	
	def get(self, google_id, default=None):
		items = list(self.get_items('google_id = ?', (google_id,)))
		if len(items) == 0:
			return default
		return items[0]

	def get_item_list_for_feed(self, feed_id):
		sql = "select google_id, title from items"
		data = None
		if feed_id is not None:
			sql += " where feed_id = ?"
			data = (feed_id,)
		cursor = self.sql(sql, data)
		for id, title in cursor:
			yield dict(id=id, name=title, count=1)
	
	def get_item_list_for_tag(self, tag):
		sql = "select google_id, title from items join feeds on items.feed_id=feeds.feed_id where feeds.tag_name = ?"
		cursor = self.sql(sql, (tag,))
		for id, title in cursor:
			yield dict(id=id, name=title, count=1)


	def get_items(self, condition=None, args=None):
		sql = "select * from items"
		if condition is not None:
			sql += " where %s" % condition
		cursor = self.sql(sql, args)
		for row_tuple in cursor:
			yield self.item_from_row(row_tuple)

	def get_feeds_and_counts(self, tag_name = None):
		condition = ""
		data = None
		if tag_name is not None:
			condition = " where feeds.tag_name = ?"
			data = (tag_name,)
		sql = (
			"select feeds.feed_id, feeds.feed_name, count(google_id) " +
			"from items inner join feeds on items.feed_id=feeds.feed_id " +
			condition +
			"group by feeds.feed_id")
		return [
			{'id':feed_id, 'name':name, 'count':count}
			for feed_id, name, count in self.sql(sql, data)]

	def get_item_count(self, tag=None, feed_id=None):
		def single_elem(cursor):
			return iter(cursor).next()[0]
		if tag is None and feed_id is None:
			return single_elem(self.sql("select count(*) from items where is_read=0"))
		elif tag is not None:
			return single_elem(self.sql("select count(*) " +
				"from items inner join feeds on items.feed_id=feeds.feed_id " +
				"where is_read=0 and feeds.tag_name=?", (tag,)))

	
	def get_tags_and_counts(self):
		sql = (
			"select feeds.tag_name, count(google_id) " +
			"from items inner join feeds on items.feed_id=feeds.feed_id " +
			"group by feeds.tag_name")

		for tag, count in self.sql(sql):
			yield {'id':tag, 'name':tag, 'count':count}

	def get_items_list(self, *args, **kwargs):
		return [x for x in self.get_items(*args, **kwargs)]

	def item_from_row(self, row_as_tuple):
		i = 0
		item = {}
		for i in range(len(row_as_tuple)):
			val = row_as_tuple[i]
			print repr(val)
			print "( type = %s)" % (i,)
			col_description = self.schema['columns'][i][1]
			if 'BOOLEAN' in col_description:
				# convert to a python boolean
				val = val == 1
			else:
				val = unicode(val)
			item[self.cols[i]] = val
		return item
	
	def close(self):
		"""close the db"""
		debug("closing DB")
		self.db.close()
		self.db = None

