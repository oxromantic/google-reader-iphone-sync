"""
Exports:
DB class
"""
import pickle, re, urllib, glob

# local imports
import app_globals
from misc import *

class DB:
	def __init__(self):
		# assume we've read everything that was left unread from last time
		self.unread = []
		self.read = self.load_previous_unread_items()
		
		# now look for still-unread items:
		for f in glob.glob(app_globals.OPTIONS['output_path'] + '/*.pdf'):
			key = self.get_key(f)
			if not key:
				continue
			self.unread.append(key)
			try_remove(key, self.read)
		
		debug("unread: " + str(self.unread))
		debug("read:   " + str(self.read))
	
	def add_item(self, item):
		self.unread.append(item.key())
		
	def get_key(self, str):
		match = re.search('\.\|\|([^|]*)\|\|\.[^.]*$', str)
		if match:
			return match.group(1)
		else:
			debug("Couldn't extract key from filename: %s" % str)
			return None
	
	def load_previous_unread_items(self):
		try:
			f = file(app_globals.OPTIONS['output_path'] + '/' + app_globals.CONFIG['pickle_file'],'r')
			ret = pickle.load(f)
			f.close()
			return ret
		except:
			print "Note: loading of previous items failed"
			return []
		
	def save(self):
		f = file(app_globals.OPTIONS['output_path'] + '/' + app_globals.CONFIG['pickle_file'],'w')
		ret = pickle.dump(self.unread, f)
		f.close()
		return ret
	
	def is_read(self, key):
		if key in self.read:
			return True
		if key in self.unread:
			return False
		return None
	
	def mark_key_as_read(self, key):
		google_id = urllib.unquote(key)
		try:
			danger("Marking item %s as read" % google_id)
			self.mark_id_as_read(google_id)
		except:
			print "Failed to mark item %s as read" % google_id
	
	def mark_id_as_read(self, google_id):
		if app_globals.OPTIONS['test']:
			print "Not telling google about anything - we're testing!"
			return
		res = app_globals.READER.set_read(google_id)
		if not res:
			print "Failed to mark item as read"
			raise Exception("Failed to mark item as read")

	
	def sync_to_google(self):
		print "Syncing with google..."
		if len(self.read) == 0: return
		print "Marking %s items as read on google-reader" % len(self.read)
		for key in self.read:
			self.mark_key_as_read(key)