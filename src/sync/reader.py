from misc import *
from output import *
from lib.GoogleReader import GoogleReader, CONST
import os

class ReaderError(StandardError):
	pass

class Reader:
	def __init__(self, user=None, password=None):
		self.gr = GoogleReader()
		self.login(user, password)

		self._tag_list = None

	def login(self, user, password):
		self.gr.identify(user, password)
		try:
			if not self.gr.login():
				raise RuntimeError("Login failed")
		except StandardError, e:
			error("error logging in: %s" % (e,))
			raise RuntimeError("Login failed (check your connection?)")
		
	def get_tag_list(self):
		if self._tag_list is None:
			tag_list = [self._tag_from_id(tag['id']) for tag in self.gr.get_tag_list()['tags']]
			self._tag_list = filter(lambda x: x is not None, tag_list)
		return self._tag_list
	tag_list = property(get_tag_list)

	def _tag_from_id(self, id):
		return id.split('/')[-1] if '/label/' in id else None
		
	def validate_tag_list(self, user_tags, strict=True):
		"""
		Raise an error if any tag (in config) does not exist in your google account
		"""
		valid_tags = []
		for utag in user_tags:
			if utag in self.tag_list:
				valid_tags.append(utag)
			elif strict:
				print "Valid tags are: %s" %(self.tag_list,)
				raise ValueError("No such tag: %r" % (utag,))
		return valid_tags

	def save_tag_list(self, output_path):
		write_file_lines(os.path.join(output_path, 'tag_list'), self.tag_list)

	def get_tag_feed(self, tag = None, count=500, oldest_first = True):
		if tag is not None:
			tag = CONST.ATOM_PREFIXE_LABEL + tag
		kwargs = {'exclude_target': CONST.ATOM_STATE_READ}
		if oldest_first:
			kwargs['order'] = CONST.ORDER_REVERSE

		return self.gr.get_feed(None, tag, count=count, **kwargs)
		
	# pass-through methods
	def passthrough(f):
		def pass_func(self, *args, **kwargs):
			return getattr(self.gr, f.__name__)(*args, **kwargs)
		return pass_func
	
	def passthrough_and_check(f):
		def pass_func(self, *args, **kwargs):
			result = getattr(self.gr, f.__name__)(*args, **kwargs)
			if result != 'OK':
				raise ReaderError("Result (%s) is not 'OK'" % (result,))
		pass_func.__name__ = f.__name__
		return pass_func

	def get_tag_feed_relations(self):
		subs = self.gr.get_subscription_list()['subscriptions']
		for sub in subs:
			tags = sub['categories']
			for tag in tags:
				tag_name = self._tag_from_id(tag['id'])
				if tag_name is not None:
					yield (tag_name, sub['id'], sub['title'])
	
	@passthrough_and_check
	def set_read(): pass

	@passthrough_and_check
	def set_unread(): pass
	
	@passthrough_and_check
	def add_star(): pass
	
	@passthrough_and_check
	def del_star(): pass
	
	@passthrough_and_check
	def add_public(): pass
	
	@passthrough_and_check
	def del_public(): pass
	
	@passthrough
	def get_feed(): pass
