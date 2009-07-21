import app_globals
import time, threading
import sys, os, time, traceback
import logging
from logging import info, debug, warning, error, exception

def ascii(s): return s.encode('ascii','ignore') if isinstance(s, unicode) else str(s)
def utf8(s):  return s.encode('utf-8','ignore') if isinstance(s, unicode) else str(s)

def status(*s):
	"""output a machine-readable status message"""
	if app_globals.OPTIONS['show_status']:
		info("STAT:%s" % ":".join(map(utf8, s)))

subtask_progress = 0
def new_subtask(length):
	global subtask_progress
	subtask_progress = 0
	status("SUBTASK_TOTAL", length)
	status("SUBTASK_PROGRESS", 0)
	
def increment_subtask():
	global subtask_progress
	subtask_progress += 1
	status("SUBTASK_PROGRESS", subtask_progress)

# level is actually an output function, i.e. one of the above
def line(level = info):
	level('-' * 50)

def log_start():
	debug("Log started at %s." % (time.ctime(),))
	debug("app version: %s" % (_get_version(),))

def _get_version():
	try:
		vfile = file(os.path.join(app_globals.OPTIONS['output_path'], 'VERSION'), 'r')
		version = vfile.readline()
		vfile.close()
		return version
	except IOError,e:
		warning("Failed to read app version: %s" % (e,))



