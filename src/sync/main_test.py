# the tested module
import main
from item import Item
from output import *

# test helpers
import test_helper
import item_test
from lib.mock import Mock
import unittest
import os
import signal
import commands
from misc import read_file, write_file

class MainTest(unittest.TestCase):
	def setUp(self):
		self.output_folder = test_helper.init_output_folder()
		self.db = app_globals.DATABASE = Mock()
	
	def tearDown(self):
		pass

	def test_item_should_be_updated_with_new_feed_name(self):
		item = Item(item_test.sample_item)
		
		db_item = Mock()
		item.tag_name = 'feedb'
		self.db.get.return_value = db_item
		db_item.is_read = False
		db_item.had_errors = False
		
		main.process_item(item)
		
		self.assertEqual(db_item.tag_name, 'feedb')
		self.assertEqual(self.db.method_calls, [('get', (item.google_id, None), {})])
		self.assertEqual(db_item.method_calls, [('update', (), {})])
	
	def test_item_with_errors_should_have_images_redownloaded(self):
		item = Item(item_test.sample_item)
		
		db_item = Mock()
		db_item.is_read = False
		db_item.had_errors = True
		self.db.get.return_value = db_item
		
		main.process_item(item)
		
		self.assertEqual(db_item.method_calls, [('redownload_images', (), {}), ('update', (), {})])
	
	def test_item_should_not_be_updated_if_it_didnt_exist_in_db(self):
		item = item_test.sample_item.copy()
		item['content'] = ''
		item = Item(item)
		
		self.db.get.return_value = None
		main.process_item(item)
		self.assertEqual(self.db.method_calls, [('get', (item.google_id, None), {}), ('add_item', (item,), {})])

	def test_setup_should_report_pid(self):
		main.proctl = Mock()
		app_globals.OPTIONS['report_pid'] = True
		self.assertRaises(SystemExit, lambda: main.setup([]))
		self.assertTrue(main.proctl.report_pid.called)

	def test_setup_should_ensure_singleton(self):
		main.proctl = Mock()
		app_globals.OPTIONS['report_pid'] = False
		main.setup(['--user=a','--password=b'])
		self.assertTrue(main.proctl.ensure_singleton_process.called)

