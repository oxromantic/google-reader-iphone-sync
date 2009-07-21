# These are some defaults and other globals.
# anything in OPTIONS can be overrided / extended by config.py in reaction to command-line or config.yml input

PLACEHOLDER = object()

CONFIG = {
	'pickle_file': '.entries.pickle',
	'test_output_dir': 'test_entries',
	'resources_path': '_resources',
	'pagefeed_feed_url_prefix': 'feed/http://pagefeed.appspot.com/feed/',
}

OPTIONS = {
	'user_config_file': 'config.plist',
	'output_path':      '/tmp/GRiS_test',
	'num_items':        300,
	'no_download':      False,
	'cautious':         False,
	'test':             False,
	'tag_list_only':    False,
	'report_pid':       False,
	'newest_first':     False,
	'show_status':      False,
	'aggressive':       False,
	'tag_list':         [],
	'user':             PLACEHOLDER,
	'password':         PLACEHOLDER,
	'ipaper_user':      PLACEHOLDER,
	'ipaper_password':  PLACEHOLDER,
	'url_save_service': 'instapaper', # can also be 'pagefeed'
	'logging':          'logging.conf',
	'logdir':           'log',
	'loglevel':         'info',
}

STATS = {
	'items':       0,
	'failed':      0,
	'new':         0,
	'read':        0,
	'reprocessed': 0,
}

# These ones get set to useful values in main.py

READER = None
DATABASE = None
URLSAVE = None
