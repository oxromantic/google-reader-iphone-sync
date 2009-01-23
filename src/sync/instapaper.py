import urllib

import app_globals

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
	
	def add_url(self):
		self._setup()
	
