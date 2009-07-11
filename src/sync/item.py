import glob
import time
import re
import urllib

# local imports
import app_globals
from misc import *
from output import *
import thread_pool

# processing modules
from lib.BeautifulSoup import BeautifulSoup
import process


def esc(s):   return urllib.quote(s)
def unesc(s): return urllib.unquote(s)

def strip_html_tags(s):
	flags = re.DOTALL | re.UNICODE
	double_tag_match = re.compile('<(?P<tagname>[a-zA-Z0-9]+)[^<>]*>(?P<content>.*?)</(?P=tagname)>', flags)
	single_tag_match = re.compile('<(?P<tagname>[a-zA-Z0-9]+)[^<>]*/>', flags)
	
	while re.search(double_tag_match, s) is not None:
		s = re.sub(double_tag_match, '\g<content>', s)
	s = re.sub(single_tag_match, '', s)
	return s

class Item:
	"""
	A wrapper around a GoogleReader item
	"""
	def __init__(self, feed_item = None, tag_name = '(unknown)', raw_data = None):
		self.had_errors = False
		if feed_item is not None:
			try: self.feed_name = feed_item['feed_name']
			except (KeyError, TypeError):
				self.feed_name = tag_name
			self.tag_name = tag_name
			self.title = strip_html_tags(utf8(feed_item['title']))
			self.title = unicode(BeautifulSoup(self.title, convertEntities = BeautifulSoup.HTML_ENTITIES))
			self.google_id = feed_item['google_id']
			self.date = time.strftime('%Y%m%d%H%M%S', time.localtime(float(feed_item['updated'])))
			self.is_read = 'read' in feed_item['categories']
			self.is_starred = 'starred' in feed_item['categories']
			self.is_shared = 'broadcast' in feed_item['categories']
			self.url = utf8(feed_item['link'])
			self.content = utf8(feed_item['content'])
			self.original_id = utf8(feed_item['original_id'])
			self.media = try_lookup(feed_item, 'media')
			self.is_pagefeed = self.any_source_is_pagefeed(map(utf8, feed_item['sources']))
			self.instapaper_url = ""
			self.is_dirty = False
			self.is_stale = False
		else:
			# just copy the dict's keys to my instance vars
			for key,value in raw_data.items():
				setattr(self, key, value)
		
		# calculated attributes that aren't stored in the DB
		self.safe_google_id = Item.escape_google_id(self.google_id)
		self.resources_path = "%s/%s/%s" % (app_globals.OPTIONS['output_path'], app_globals.CONFIG['resources_path'], self.safe_google_id)
		self.basename = self.get_basename()
	
	@staticmethod
	def unescape_google_id(safe_google_id):
		return urllib.unquote(safe_google_id)

	@staticmethod
	def escape_google_id(unsafe_google_id):
		return urllib.quote(unsafe_google_id, safe='')

	def get_basename(self):
		"""A filesystem-safe key, unique to this item"""
		return utf8(
			self.date + ' ' +
			filter(lambda x: x not in '"\':#!+/$\\?*', ascii(self.title))[:120] + ' .||' +
			self.safe_google_id + '||' )

	def soup_setup(self):
		self.soup = BeautifulSoup(self.content)
		try:
			self.base = url_dirname(self.original_id)
		except TypeError:
			self.base = None
	
	def soup_teardown(self):
		self.soup 
		self.content = self.soup.prettify()
		
	def process(self):
		debug("item %s -> process()" % self.title)
		self.soup_setup()
		thread_pool.ping()
		
		# process
		debug("item %s -> insert_alt_text()" % self.title)
		process.insert_alt_text(self.soup)
		thread_pool.ping()
		
		self.download_images(need_soup = False)
		thread_pool.ping()
		
		# save changes back as content
		self.soup_teardown()
	
	def redownload_images(self):
		self.had_errors = False
		self.download_images()
		self.update()
	
	def download_images(self, need_soup=True):
		self.had_errors = False

		if need_soup:
			self.soup_setup()
		
		try: media = self.media
		except AttributeError: media = None

		if media is not None:
			success = process.insert_enclosure_images(self.soup, url_list = self.media)
			if not success:
				self.had_errors = True
		
		debug("item %s -> download_images()" % (self.title,))
		success = process.download_images(self.soup,
			dest_folder = self.resources_path,
			href_prefix = app_globals.CONFIG['resources_path'] + '/' + self.safe_google_id + '/',
			base_href = self.base)
		if not success:
			self.had_errors = True

		if need_soup:
			self.soup_teardown()
	
	def save(self):
		app_globals.DATABASE.add_item(self)
	
	def update(self):
		app_globals.DATABASE.update_content_for_item(self)

	def delete(self):
		app_globals.DATABASE.remove_item(self)
		for f in glob.glob(app_globals.OPTIONS['output_path'] + '/*.' + self.safe_google_id + '.*'):
			rm_rf(f)
		rm_rf(self.resources_path)
	
	def get_instpapaer_urls(self):
		return set(self.instapaper_url.split('|'))
	instapaper_urls = property(get_instpapaer_urls)
	
	def save_to_web(self):
		print "saving item..."
		if not self.is_dirty:
			return
		
		# instapaper / pagefeed URLs
		if self.instapaper_url and len(self.instapaper_url) > 0:
			app_globals.INSTAPAPER.add_urls(self.instapaper_urls)
			self.instapaper_url = ''
		
		# read status
		if self.is_read:
			self._google_do(app_globals.READER.set_read)

		# stars
		if self.is_starred:
			self._google_do(app_globals.READER.add_star)
		
		# share
		if self.is_shared:
			self._google_do(app_globals.READER.add_public)
		
		self.delete_from_web_if_required()
		self.is_dirty = False

	def still_needed(self):
		is_unread = not self.is_read
		return is_unread or self.is_starred or self.is_shared
	
	def any_source_is_pagefeed(self, sources):
		source_is_pagefeed = lambda source: source.startswith(app_globals.CONFIG['pagefeed_feed_url_prefix'])
		return any(map(source_is_pagefeed, sources))
	
	def delete_from_web_if_required(self):
		if self.still_needed() or not self.is_pagefeed:
			return
		
		try:
			app_globals.INSTAPAPER.delete(url=self.url)
		except AttributeError:
			debug("url save mechanism has no delete function")
			return

	def _google_do(self, action):
		return action(self.google_id)
