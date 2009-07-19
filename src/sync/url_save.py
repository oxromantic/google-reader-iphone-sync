INSTAPAPER = 'instapaper'
PAGEFEED = 'pagefeed'
OPTS_KEY = 'url_save_service'

import app_globals
from output import debug

def get_active_service():
	service_name = app_globals.OPTIONS[OPTS_KEY]
	if service_name == PAGEFEED:
		debug("URL SAVE: pagefeed mode")
		from pagefeed import PageFeed
		return PageFeed()
	elif service_name == INSTAPAPER:
		debug("URL SAVE: instapaper mode")
		from instapaper import Ipaper
		return Ipaper()
	else:
		raise ValueError("%s is %s (expected %s)" % (
			OPTS_KEY, service_name,
			' or '.join((INSTAPAPER, PAGEFEED))))

