import urllib2
import urllib

import app_globals
from output import *
from auth import LoginError

class Ipaper(object):
	def __init__(self):
		self.is_setup = False
	
	def _setup(self):
		"""ensure login details are setup"""
		if not self.is_setup:
			self.user = app_globals.OPTIONS['ipaper_user']
			self.password = app_globals.OPTIONS['ipaper_password']
			self.is_setup = True
		
	def missing(self, obj):
		return (not isinstance(obj, str)) or len(obj) == 0
	
	def add_urls(self, urls):
		map(self.add_url, urls)
	
	def add_url(self, url, title = None):
		self._setup()
		if self.missing(self.user) or not isinstance(self.password, str):
			info("WARNING: Instapaper url dropped: %s" % (url,))
			return

		debug("saving instapaper URL: %s" % (url,))
		
		post_url = 'https://www.instapaper.com/api/add'
		params = {
			'username': self.user,
			'password': self.password,
			'url': url
			}
		if title:
			params['title'] = title
		else:
			params['auto-title'] = '1'
		
		self._post(post_url, params)
	
	def _post(self, url, params):
		post_data = urllib.urlencode(params)
		
		result = None
		try:
			result = urllib2.urlopen(url, data=post_data)
		except urllib2.HTTPError, e:
			result = e.code
		if result != 201:
			if e.code == 403: # permission denied
				raise RuntimeError("instapaper login failed")
			raise RuntimeError("instapaper post failed: response=%s" % (result))

