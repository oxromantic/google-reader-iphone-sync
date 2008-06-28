import glob, time, os, re, urllib

# local imports
import app_globals
from misc import *
import template

# processing modules
from lib.BeautifulSoup import BeautifulSoup
from process import insert_alt_text


def remove_the_damn_html_entities(s):
	# surely there should be a library method somewhere to decode these. But for our purposes we can just ditch them.
	return re.sub('&.{2,4};','',s)

def esc(s):   return urllib.quote(string)
def unesc(s): return urllib.unquote(s)

def ascii(s): return s.encode('ascii','ignore') if isinstance(s, unicode) else s
def utf8(s):  return s.encode('utf-8','ignore') if isinstance(s, unicode) else s


class Item:
	"""
	A wrapper around a GoogleReader item
	"""
	def __init__(self, feedItem):
		self.item = feedItem

	def key(self):
		return urllib.quote(self.item['google_id'],safe='')
		
	def basename(self):
		tag_str = ''
		for cat in self.item['categories']:
			if re.search('ipod$', cat, re.I) is not None:
				tag_str = '[txt] '
		return utf8(
		time.strftime('%Y-%m-%d', time.localtime(self.item['updated'])) + ' ' + tag_str +
			filter(lambda x: x not in '"\':+/$\\?*', ascii(remove_the_damn_html_entities(self.item['title'])))[:120] + ' .||' +
			self.key() + '||' )
	
	def process(self):
		self.item['soup'] = BeautifulSoup(self.item['content'])
		self.item = insert_alt_text(self.item)
		self.item['content'] = self.item['soup'].prettify()
	
	def output(self):
		base = app_globals.OPTIONS['output_path'] + '/' + self.basename()

		render_object = {
			'title_link':  '<a href="' + utf8(self.item['link']) + '">' + utf8(self.item['title']) + '</a>',
			'title':       utf8(self.item['title']),
			'content':     utf8(self.item['content']),
		}

		# create the "via" link
		try:
			render_object['via'] = ' via ' + re.sub('.*://', '', self.item['sources'].keys()[0]).replace('/',' / ').replace('=',' = ') + '<br /><br />'
		except:
			pass
		
		debug("rendering item to %s using template file %s" % (base + '.html', 'template/item.html'))
		template.create(render_object, 'template/item.html', base + '.html')

		try:
			debug("converting to pdf")
			# convert to pdf:
			cmd = 'python src/html2pdf.py ' + \
				'-w ' + str(int(app_globals.OPTIONS['screen_width'])) + \
				' -h '+ str(int(app_globals.OPTIONS['screen_height'])) + \
				' "' + base + '.html" "'+ base +'.pdf"'
			debug("command: " + cmd)
			# i like to shell out for this, because sometimes it segfaults. I guess pyObjC isn't 100% stable...
			ret = os.system(cmd)
			debug("command returned: " + str(ret))
			if ret == 0:
				app_globals.DATABASE.add_item(self)
			else:
				print "pdf conversion failed"
		finally:
			if not app_globals.OPTIONS['test']:
				# cleanup
				os.remove(base + '.html')
	
	def is_read(self):
		return 'read' in self.item['categories']
	
	def delete(self):
		for f in glob.glob(app_globals.OPTIONS['output_path'] + '/*.' + self.key() + '.*'):
			print "Removing file: " + f
			danger('remove file')
			os.remove(f)