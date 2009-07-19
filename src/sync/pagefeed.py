import urllib
import urllib2

from output import *

import app_globals
from lib.app_engine_auth import AppEngineAuth

# BASE_URI = 'http://localhost:8082/'
BASE_URI = 'http://pagefeed.appspot.com/'
APP_NAME = "pagefeed-1.0"

class PageFeed(object):
	def __init__(self, email=None, password=None):
		self.email = email or app_globals.OPTIONS['user']
		self.password = password or app_globals.OPTIONS['password']
		self.auth_key = None
	
	def _setup(self):
		if self.auth_key is None:
			debug("authorising to app engine")
			auth = AppEngineAuth(self.email, self.password)
			self.auth_key = auth.login(APP_NAME, BASE_URI)
	
	def add_urls(self, urls):
		map(self.add, urls)

	def add(self, url):
		self._setup()
		debug("adding url to pagefeed: %s" % (url,))
		self._post('page/', params={'url':url})
	
	def delete(self, url):
		self._setup()
		debug("deleting url from pagefeed: %s" % (url,))
		try:
			self._post('page/del/', params={'url':url})
		except urllib2.HTTPError, e:
			if e.code == 404:
				info("couldn't delete - no such URL")
			else:
				raise

	# ------------------------------

	def _post(self, relative_uri, params={}):
		req = urllib2.Request(BASE_URI + relative_uri, data=self._data(params))
		return self._load(req)
	
	def _load(self, request):
		try:
			response = urllib2.urlopen(request)
			return response.read()
		except urllib2.HTTPError, e:
			puts("The request failed (response code: %s)" % (e.code,))
			raise

	def _data(self, params):
		params = params.copy()
		params['auth'] = self.auth_key
		encoded = urllib.urlencode(params)
		return encoded

	def _get(self, relative_uri, params={}):
		req = urllib2.Request(BASE_URI + relative_uri + '?' + self._data(params))
		return self._load(req)
	
