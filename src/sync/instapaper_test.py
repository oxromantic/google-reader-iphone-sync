from mocktest import *
from instapaper import Ipaper
from auth import LoginError
import test_helper
import urllib
import urllib2
from misc import *

class InstapaperTest(TestCase):
	def setUp(self):
		# test_helper.init_output_folder()
		app_globals.OPTIONS['ipaper_user'] = 'ipaper_user'
		app_globals.OPTIONS['ipaper_password'] = 'ipaper_password'
		self.ip = Ipaper()
	
	def httpStatus(self, code):
		class FakeFP(object):
			def read(self):
				return EOFError
			def readline(self):
				return EOFError
		return urllib2.HTTPError('url',code,'msg','headers',FakeFP())
		
	def test_should_add_url_with_title(self):
		def check_args(url, data):
			self.assertEqual(url, 'https://www.instapaper.com/api/add')
			pairs = data.split('&')
			self.assertEqual(sorted(pairs), sorted([
				'username=ipaper_user',
				'password=ipaper_password',
				'url=http%3A%2F%2Flocalhost%2F',
				'title=the+title']))
			return True
		
		mock_on(urllib2).urlopen.raising(self.httpStatus(201)).is_expected.where_args(check_args)
		self.ip.add_url('http://localhost/', 'the title')

	def test_should_add_url_without_title(self):
		def check_args(url, data):
			self.assertEqual(url, 'https://www.instapaper.com/api/add')
			pairs = data.split('&')
			self.assertEqual(sorted(pairs), sorted([
				'username=ipaper_user',
				'password=ipaper_password',
				'url=http%3A%2F%2Flocalhost%2F',
				'auto-title=1']))
			return True
		
		mock_on(urllib2).urlopen.raising(self.httpStatus(201)).is_expected.where_args(check_args)
		self.ip.add_url('http://localhost/')
	
	def test_should_silently_fail_if_username_and_pass_are_blank(self):
		app_globals.OPTIONS['ipaper_user'] = ''
		app_globals.OPTIONS['ipaper_password'] = ''
		mock_on(urllib2).urlopen.is_expected.no_times()
		self.ip.add_url('http://localhost/', 'the title')
		
	def test_should_silently_fail_if_username_and_pass_are_none(self):
		app_globals.OPTIONS['ipaper_user'] = None
		app_globals.OPTIONS['ipaper_password'] = None
		mock_on(urllib2).urlopen.is_expected.no_times()
		self.ip.add_url('http://localhost/', 'the title')
		
