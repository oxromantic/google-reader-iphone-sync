"""
Exports:
DB class
"""
import glob
import os

# local imports
import config
import app_globals
from misc import *
from output import *
from item import Item

import sqlite3 as sqlite

# to support data migration, we currently have all versions / modifications to the schema
# hopefully this won't become too ungainly
schema_history = [
	'CREATE TABLE items(google_id TEXT primary key, date TIMESTAMP, url TEXT, original_id TEXT, title TEXT, content TEXT, feed_name TEXT, is_read BOOLEAN, is_starred BOOLEAN, is_dirty BOOLEAN default 0)',
	'CREATE UNIQUE INDEX item_id_index on items(google_id)',
	'ALTER TABLE items ADD COLUMN had_errors BOOLEAN default 0',
	'ALTER TABLE items ADD COLUMN is_stale BOOLEAN default 0',
	'ALTER TABLE items ADD COLUMN tag_name BOOLEAN default ""',
	'ALTER TABLE items ADD COLUMN is_shared BOOLEAN default 0',
	'ALTER TABLE items ADD COLUMN instapaper_url TEXT default ""',
	'ALTER TABLE items ADD COLUMN is_pagefeed BOOLEAN default 0',
	]

class VersionDB:
	@staticmethod
	def version(db):
		version = 0
		tables = map(first, db.execute('select tbl_name from sqlite_master').fetchall())
		if 'db_version' in tables:
			version = int(first(db.execute('select version from db_version').fetchone()))
		else:
			db.execute('CREATE TABLE db_version(version INT)')
			db.execute('INSERT INTO db_version(version) VALUES (0)')
		return version

	@staticmethod
	def migrate(db, schema_history):
		version = VersionDB.version(db)
		unapplied_schema_steps = schema_history[version:]
		if len(unapplied_schema_steps) > 0:
			info("Your database is at version %s, the latest is version %s. Upgrading" % (version, len(schema_history)))
			print unapplied_schema_steps
			for step in unapplied_schema_steps:
				debug("Appling the following query to your database:\n%s" % (step,))
				db.execute(step)
				version += 1
				db.execute('update db_version set version = ?', (version,))
			debug("database is up to date! (version %s)" % len(schema_history))
			db.commit()
		return len(unapplied_schema_steps)


class DB:
	def __init__(self, filename = 'items.sqlite'):
		if app_globals.OPTIONS['test']:
			filename = os.path.dirname(filename) + 'test_' + os.path.basename(filename)
		self.filename = filename = os.path.join(app_globals.OPTIONS['output_path'], os.path.basename(filename))
		debug("loading db: %s" % filename)
		self.db = sqlite.connect(filename)

		# commit immediately after statements.
		# doing commits every now and then seems buggy, and we don't need it.
		self.db.isolation_level = "IMMEDIATE"

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
			],
			'indexes' : [ ('item_id_index', 'items(google_id)') ]
		}
		self.cols = [x for (x,y) in self.schema['columns']]
		self.setup_db()

	def reload(self):
		"""
		reload the database
		"""
		self.close()
		self.db = sqlite.connect(self.filename)

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
	
	def erase(self):
		if not app_globals.OPTIONS['test']:
			raise Exception("erase() called, but we're not in test mode...")
		self.sql('delete from items')

	def reset(self):
		self.erase()
		self.setup_db()
	
	def tables(self):
		return [row[0] for row in self.db.execute('select name from sqlite_master where type = "table"')]

	def setup_db(self):
		global schema_history
		if VersionDB.migrate(self.db, schema_history) > 0:
			self.reload()
		
	def add_item(self, item):
		self.sql("insert into items (%s) values (%s)" % (', '.join(self.cols), ', '.join(['?'] * len(self.cols))),
			[getattr(item, attr) for attr in self.cols])
	
	def update_content_for_item(self, item):
		self.sql("update items set content=?, tag_name=?, is_stale=? where google_id=?", (item.content, item.tag_name, False, item.google_id))
	
	def remove_item(self, item):
		google_id = item.google_id
		self.sql("delete from items where google_id = ?", (google_id,))
	
	def update_item(self, item):
		self.sql("update items set is_read=?, is_starred=?, is_shared=?, is_dirty=?, instapaper_url=? where google_id=?",
			(item.is_read, item.is_starred, item.is_shared, item.is_dirty, item.instapaper_url, item.google_id));

	def get_items(self, condition=None, args=None):
		sql = "select * from items"
		if condition is not None:
			sql += " where %s" % condition
		cursor = self.sql(sql, args)
		for row_tuple in cursor:
			yield self.item_from_row(row_tuple)
	
	def get_item_count(self, condition=None, args=None):
		sql = "select count(*) from items"
		if condition is not None:
			sql += " where %s" % condition
		cursor = self.sql(sql, args)
		return cursor.next()[0]

	def get_items_list(self, *args, **kwargs):
		return [x for x in self.get_items(*args, **kwargs)]

	def item_from_row(self, row_as_tuple):
		i = 0
		item = {}
		for i in range(len(row_as_tuple)):
			val = row_as_tuple[i]
			col_description = self.schema['columns'][i][1]
			if 'BOOLEAN' in col_description:
				# convert to a python boolean
				val = val == 1
			else:
				val = unicode(val)
			item[self.cols[i]] = val
		return Item(raw_data = item)
	
	def cleanup(self):
		"""Clean up any stale items / resources"""
		self.cleanup_stale_items()
		self.cleanup_resources_directory()
		
	def close(self):
		"""close the db"""
		debug("closing DB")
		# despite our insistance of "IMMEDIATE" isolation level, this seems to be necessary
		self.db.commit()
		self.db.close()
		self.db = None

	def sync_to_google(self):
		info("Syncing with google...")
		status("SUBTASK_TOTAL", self.get_item_count('is_dirty = 1'))
		item_number = 0
		for item in self.get_items('is_dirty = 1'):
			debug('syncing item state \"%s\"' % item.title)
			item.save_to_web()
			self.update_item(item)

			item_number += 1
			status("SUBTASK_PROGRESS",item_number)

		for item in self.get_items('is_read = 1'):
			debug('deleting item \"%s\"' % item.title)
			item.delete()
		danger("about to delete %s read items from db" % self.get_item_count('is_read = 1'))
		self.sql('delete from items where is_read = 1')
		
	def prepare_for_download(self):
		self.sql('update items set is_stale = ?', (True,))
	
	def cleanup_stale_items(self):
		self.sql('delete from items where is_stale = ?', (True,))
	
	def cleanup_resources_directory(self):
		res_prefix = "%s/%s/" % (app_globals.OPTIONS['output_path'], app_globals.CONFIG['resources_path'])
		glob_str = res_prefix + "*"
		current_keys = set([os.path.basename(x) for x in glob.glob(glob_str)])
		unread_keys = set([Item.escape_google_id(row[0]) for row in self.sql('select google_id from items where is_read = 0')])

		current_but_read = current_keys.difference(unread_keys)
		if len(current_but_read) > 0:
			info("Cleaning up %s old resource directories" % len(current_but_read))
			danger("remove %s old resource directories" % len(current_but_read))
			for key in current_but_read:
				rm_rf(res_prefix + key)

if __name__ == '__main__':
	print "running DB migration..."
	app_globals.OPTIONS['loglevel'] = 'DEBUG'
	app_globals.OPTIONS['output_path'] = '.'
	config.init_logging()
	db = DB()
	db.close()
