#!/usr/bin/env python
# general includes
import sys, glob, urllib2, os, commands

# local includes
import config
from db import DB
from item import Item
import proctl
import signal
from misc import *
from output import *
from lib.GoogleReader import GoogleReader, CONST
import app_globals
import template
from reader import Reader
import url_save
from thread_pool import ThreadPool

TASK_PROGRESS = 0
CANCELLED = False

def new_task(description=""):
	global TASK_PROGRESS
	status("TASK_PROGRESS", TASK_PROGRESS, description)
	TASK_PROGRESS += 1

def handle_signal(signum, stack):
	global CANCELLED
	print "Signal caught: %s" % (signum,)
	status("TASK_PROGRESS", TASK_PROGRESS, "Cancelled")
	CANCELLED = True
	cleanup()
	sys.exit(2)
	
def cleanup():
	if app_globals.DATABASE is not None:
		app_globals.DATABASE.close()
	app_globals.URLSAVE = None
	app_globals.READER = None
	
def init_signals():
	pass
	# signal.signal(signal.SIGINT, handle_signal)
	# signal.signal(signal.SIGTERM, handle_signal)

def save_db_state():
	debug("saving database state...")
	app_globals.DATABASE.close()
	app_globals.DATABASE = DB()

def execute():
	"""
	Logs in, syncs and downloads new items
	"""
	steps = 3
	download_steps = 0
	if not app_globals.OPTIONS['no_download']:
		download_steps = len(app_globals.OPTIONS['tag_list'])
		if download_steps < 1: download_steps = 1
		steps += download_steps
	
	status("TASK_TOTAL",steps)
	new_task("Authorizing")
	
	ensure_dir_exists(app_globals.OPTIONS['output_path'])
	ensure_dir_exists(app_globals.OPTIONS['output_path'] + '/' + app_globals.CONFIG['resources_path'])
	
	app_globals.URLSAVE = url_save.get_active_service()
	
	app_globals.READER = Reader()
	app_globals.READER.save_tag_list()
	if app_globals.OPTIONS['tag_list_only']:
		info("Got all tags.")
		return

	app_globals.OPTIONS['tag_list'] = app_globals.READER.validate_tag_list(app_globals.OPTIONS['tag_list'], False)

	new_task("Pushing status")

	line()
	app_globals.DATABASE = DB()
	
	# we now have something we need to clean up on interrupt:
	init_signals()
	
	app_globals.DATABASE.sync_to_google()
	
	if app_globals.OPTIONS['no_download']:
		info("not downloading any new items...")
	else:
		app_globals.DATABASE.prepare_for_download()
		download_new_items()
		new_task("Cleaning up old resources")
		app_globals.DATABASE.cleanup() # remove old _resources files

def download_feed(feed, feed_tag):
	new_subtask(len(feed) * 2)
	item_thread_pool = ThreadPool()
	for entry in feed.get_entries():
		increment_subtask()
	
		app_globals.STATS['items'] += 1

		if entry is None:
			app_globals.STATS['failed'] += 1
			error(" ** FAILED **")
			debug("(entry is None)")
			continue
		
		item = Item(entry, feed_tag)
		process_item(item, item_thread_pool)
		item_thread_pool.collect()
	item_thread_pool.collect_all()

def error_reporter_for_item(item):
	def error_report(exception, tb = None):
		error(" ** FAILED **: ", exc_info=True)
		app_globals.STATS['failed'] += 1
	return error_report

def process_item(item, item_thread_pool = None):
	db_item = app_globals.DATABASE.get(item.google_id, None)
	name = item.basename
	
	item_is_read = item.is_read or (db_item is not None and db_item.is_read)
	if item_is_read:
		# item has been read either online or offline
		debug("READ: " + name)
		app_globals.STATS['read'] += 1
		danger("About to delete item")
		item.delete()
		increment_subtask()
		return

	if db_item is not None:
		# we aready know about it - update any necessary info
		if db_item.had_errors or db_item.tag_name != item.tag_name:
			app_globals.STATS['reprocessed'] += 1
			debug("setting %s tag name to %s" % (db_item, item.tag_name))
			db_item.tag_name = item.tag_name
			if db_item.had_errors:
				debug("reprocessing erroneous item: %s" % (item.title,))
				db_item.redownload_images()
		db_item.update()
		increment_subtask()
	else:
		try:
			info("NEW: " + item.title)
			danger("About to output item")
			app_globals.STATS['new'] += 1
			if item_thread_pool is None:
				item.process()
				item.save()
				increment_subtask()
			else:
				def success_func():
					increment_subtask()
					item.save()
				item_thread_pool.spawn(item.process, on_success = success_func, on_error = error_reporter_for_item(item))

		except StandardError,e:
			error_reporter_for_item(item)(e)
		
def download_new_items():
	"""
	Downloads new items from google reader across all feeds
	"""
	tag_list = app_globals.OPTIONS['tag_list']

	# special case: no tags specified so we download the global set
	if len(tag_list) == 0:
		tag_list = [None]
	
	status("SUBTASK_TOTAL", len(tag_list) * app_globals.OPTIONS['num_items'])

	for feed_tag in tag_list:
		line()
		save_db_state()
		_feed_tag = "All Items" if feed_tag is None else feed_tag
		new_task("Downloading tag \"%s\"" % (_feed_tag,))
		info("Fetching maximum %s items from feed %s" % (app_globals.OPTIONS['num_items'], _feed_tag))
		feed = app_globals.READER.get_tag_feed(feed_tag, oldest_first = not app_globals.OPTIONS['newest_first'])
		download_feed(feed, _feed_tag)
		
	line()
	
	info("%s NEW items" % app_globals.STATS['new'])
	info("%s items marked as read" % app_globals.STATS['read'])
	if app_globals.STATS['reprocessed'] > 0:
		info("%s items reprocessed because of previously failed image downloads" % (app_globals.STATS['reprocessed']))
	if app_globals.STATS['failed'] > 0:
		warning("%s items failed to parse" % app_globals.STATS['failed'])

def setup(opts=None):
	"""Parse options. If none given, opts is set to sys.argv"""
	if opts is None:
		opts = sys.argv[1:]
	config.bootstrap(opts)
	config.init_logging()
	config.load()
	config.parse_options(opts)
	ensure_dir_exists(app_globals.OPTIONS['output_path'])
	log_start()
	if app_globals.OPTIONS['report_pid']:
		proctl.report_pid()
		exit(0)
	config.check()
	proctl.ensure_singleton_process()
	init_signals()

def main():
	"""
	Main program entry point - loads config, parses otions and kicks off the sync process
	"""
	setup()
	execute()
	cleanup()
	print "Sync complete."
	return 0

if __name__ == '__main__':
	exitstatus = 1
	try:
		exitstatus = main()
	except StandardError, e:
		debug('unhandled error in main()', exc_info=True)
		if not CANCELLED:
			error("ERROR: %s" % (e,))
		exitstatus = 2
	except KeyboardInterrupt:
		info("cancelled - cleaning up")
		cleanup()
		print "Cancelled."
	sys.exit(exitstatus)

