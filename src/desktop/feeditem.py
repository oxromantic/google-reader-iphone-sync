class FeedItem(object):
	def __init__(self, attrs):
		for k,v in attrs:
			setattr(self, k, v)
	
	def html(self):
			# self.feed_name = tag_name
			# self.tag_name = tag_name
			# self.title = strip_html_tags(feed_item['title'])
			# self.title = unicode(BeautifulSoup(self.title, convertEntities = BeautifulSoup.HTML_ENTITIES))
			# self.google_id = feed_item['google_id']
			# self.date = time.strftime('%Y%m%d%H%M%S', time.localtime(float(feed_item['updated'])))
			# self.is_read = 'read' in feed_item['categories']
			# self.is_starred = 'starred' in feed_item['categories']
			# self.is_shared = 'broadcast' in feed_item['categories']
			# self.url = feed_item['link']
			# self.content = feed_item['content']
			# self.original_id = feed_item['original_id']
			# self.media = try_lookup(feed_item, 'media')
			# self.is_dirty = False
			# self.is_stale = False
		return """
			<html>
				<head>
					<link rel='stylesheet' href='template/style.css' type='text/css' />
				</head>
				<body>
					<div class='post-info header'>
						<h1 id='title'>
							<a href='%s'>%s</a>""" % (self.url, self.title) + """
						</h1>
						<div class='via'>
							%s""" % (self.feed_name,) + """
						</div>
					</div>
					<div class='content'><p>
						%s""" % (self.content,) + """
					</div>
					<div class='post-info footer'>
						<div class='date'>
							<b>%s</b> in <b>%s</b>""" % (self.date, self.tag_name) + """
						</div>
						<div>
							(<i>%s</i>)""" % (self.url,) + """
						</div>
					</div>
				</body>
			</html>"""

