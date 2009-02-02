import urllib2
import urllib

import app_globals
from output import *

class Ipaper(object):
	def __init__(self):
		self.is_setup = false
	
	def _setup(self):
		"""ensure login details are setup"""
		if not self.is_setup:
			self.user = app_globals.OPTIONS['ipaper_user']
			self.password = app_globals.OPTIONS['ipaper_password']
			if not (isinstance(self.user, str) and isinstance(self.password, str):
				raise RuntimeError("Instapaper username or password not set")
			self.is_setup = True
	
	def add_url(self, url, title = None):
		self._setup()
		
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

		self._post(post_url, post_data)
	
	def _post(self, url, params):
		post_data = urllib.urlencode(params)
		
		result = None
		try:
			result = urllib2.urlopen(url, data=post_data)
		except urllib2.HTTPError, e:
			result = e.code
		if result != 201:
			if len(self.user) == len(self.password) == 0:
				info("WARNING: Instapaper url dropped: %s" % (params['url'],))
				return
			if e.code == 403: # permission denied
				raise RuntimeError("instapaper login failed")
			raise RuntimeError("instapaper post failed: response=%s" % (result))

