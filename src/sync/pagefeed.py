import os
import urllib
import urllib2
import cookielib

# BASE_URI = 'http://localhost:8082/'
BASE_URI = 'http://pagefeed.appspot.com/'
APP_NAME = "pagefeed-1.0"

class PageFeed(object):
	def __init__(self, email, password):
		self.email = email
		auth = AppEngineLogin(email, password)
		self.auth_key = auth.login(APP_NAME, BASE_URI)

	def add(self, url):
		self._post('page/', params={'url':url})
	
	def delete(self, url):
		self._post('page/del/', params={'url':url})

	# ------------------------------

	def _post(self, relative_uri, params={}):
		req = urllib2.Request(BASE_URI + relative_uri, data=self._data(params))
		return self._load(req)
	
	def _load(self, request):
		response = urllib2.urlopen(request)
		return response.read()

	def _data(self, params):
		params = params.copy()
		params['auth'] = self.auth_key
		encoded = urllib.urlencode(params)
		return encoded

	def _get(self, relative_uri, params={}):
		req = urllib2.Request(BASE_URI + relative_uri + '?' + self._data(params))
		return self._load(req)
	
