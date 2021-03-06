from misc import *
from output import *
import app_globals
import re

import pdb

def update(obj, input_filename, output_filename = None, restrict_to=None):
	if output_filename is None:
		output_filename = input_filename
	_process(obj, input_filename, output_filename, restrict_to)

def update_template(template_filename, input_filename, output_filename=None):
	"""
	update the output of a previous template to a new template version
	"""
	if output_filename is None:
		output_filename = input_filename
	obj = _extract_templated_values(input_filename)
	_process(obj, template_filename, output_filename, None)
	
def create(obj, input_filename, output_filename = None, restrict_to=None):
	if output_filename is None:
		outut_filename = input_filename + ".html"
	_process(obj, input_filename, output_filename, restrict_to)

def get_str(obj):
	"""
	Get a string value from an arbitrary object.
	If it's callable, try to call it. If that fails, just convert it to a string.
	"""
	if obj is None:
		return ""
	try:
		res = str(obj())
	except TypeError:
 		res = str(obj)
	return res

def process_string(subject_str, obj, restrict_to = None):
	r"""
	Replaces {variable} substitutions that are within HTML comments.
	The replacement includes html-comment markers so that the value can be replaced / updated if desired.

	>>> process_string("<!--{content}-->", {'content':"la la la"})
	'<!--{content=}-->la la la<!--{=content}-->'

	>>> process_string('<!--{content=}-->previous\ncontent<!--{=content}-->', {'content':"new value"})
	'<!--{content=}-->new value<!--{=content}-->'

	# the restrict_to argument limits the set of keys that will be interpreted:
	>>> process_string("<!--{content}-->", {'content':"new value"}, ['other_key'])
	'<!--{content}-->'
	>>>
	"""
	# do expanded first, otherwise you'll expand it and match it again with expanded_re!
	for matcher_func in (_expanded_regex, _unexpanded_regex):
		matcher = matcher_func() # evaluate it
		matches = matcher.finditer(subject_str)
		for match in matches:
			object_property = match.groupdict()['tag']
			debug("object property: " + object_property)
			if (restrict_to is None or object_property in restrict_to):
				attr = get_attribute(obj, object_property)
				if attr is not None:
					# do the replacement!
					debug("substituting property: " + object_property)
					replacement_matcher = matcher_func(object_property)
					subject_str = replacement_matcher.sub('<!--{\g<tag>=}-->' + get_str(attr) + '<!--{=\g<tag>}-->', subject_str)
				else:
					debug("object does not respond to " + object_property)
				
	return subject_str

def extract_values(contents):
	"""
	grab a hash of values that were used to create the given
	output string (from a previous template render)
	
	>>> extract_values('fkdjlf<!--{something=}-->Value!<!--{=something}-->dsds')
	{'something': 'Value!'}
	"""
	obj = {}
	matches = _expanded_regex().finditer(contents)
	for match in matches:
		key = match.groupdict()['tag']
		content = match.groupdict()['content']
		obj[key] = content
	return obj


default_tagex = '[a-zA-Z0-9_]+'
def _unexpanded_regex(tagex = None):
	global default_tagex
	if tagex is None:
		tagex = default_tagex
	return re.compile('<!--\{(?P<tag>' + tagex + ')\}-->')

def _expanded_regex(tagex = None):
	global default_tagex
	if tagex is None:
		tagex = default_tagex
	return re.compile('<!--\{(?P<tag>' + tagex + ')=\}-->(?P<content>.*?)<!--\{=(?P=tag)\}-->', re.DOTALL) # the dot can match newlines


####################################################################################
# internal methods only below - use the above methods to interact with this module #
####################################################################################

def _process(obj, input_filename, output_filename, restrict_to):
	infile = file(input_filename, 'r')
	contents = infile.read()
	contents = process_string(contents, obj, restrict_to)
	infile.close()
	outfile = file(output_filename, 'w')
	outfile.write(contents)

def _extract_templated_values(input_filename):
	infile = file(input_filename, 'r')
	contents = infile.read()
	obj = extract_values(contents)
	infile.close()
	return obj

def get_attribute(obj, attr):
	"""
	Much like the built-in getattr, except:
	 - it returns None on failure
	 - it tries dictionary lookups if no attribute is found
	
	>>> class Something:
	... 	def __init__(self):
	... 		self.internal_var = 'moop'

	>>> get_attribute(Something(), 'internal_var')
	'moop'

	>>> get_attribute({'test_var':'test_val'}, 'test_var')
	'test_val'
	"""
	
	ret = None
	try:
		ret = getattr(obj, attr)
	except AttributeError:
		try:
			ret = obj[attr]
		except (TypeError, KeyError):
			pass
	return ret
