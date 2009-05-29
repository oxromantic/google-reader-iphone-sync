#import "FeedItem.h"
#import "TCHelpers.h"

@implementation FeedItem
@synthesize google_id, original_id, url, date, title, content, feed_name, tag_name, is_read, is_starred, is_shared, is_dirty;
- (id) initWithId: (NSString *) ngoogle_id
	originalId: (NSString *) noriginal_id
	date: (NSString *) ndate
	url: (NSString *) nurl
	title: (NSString *) ntitle
	content: (NSString *) ncontent
	feedName: (NSString *) nfeed_name
	tagName: (NSString *) ntag_name
	is_read: (BOOL) nis_read
	is_starred: (BOOL) nis_starred
	is_shared: (BOOL) nis_shared
	ipaper_url: (NSString *) nipaper_url
	db: (id) ndb
{
	self = [super init];
	google_id = [ngoogle_id retain];
	original_id = [noriginal_id retain];
	date = [ndate retain];
	url = [nurl retain];
	title = [ntitle retain];
	content = [ncontent retain];
	source_db = [ndb retain];
	feed_name = [nfeed_name retain];
	tag_name = [ntag_name retain];
	ipaper_url = [nipaper_url retain];

	// booleans don't need no retaining
	is_read = nis_read;
	is_starred = nis_starred;
	is_shared = nis_shared;
	is_dirty = NO;
	
	sticky_read_state = NO;
	return self;
}

- (BOOL) hasChildren { return NO; }

- (void) save {
	[source_db updateItem:self];
}

- (NSString *) domainName {
	NSString * domain = original_id;
	NSRange protocol_sep = [domain rangeOfString: @"://"];
	NSRange domainRange;
	if(protocol_sep.length > 0){
		domainRange.location = (protocol_sep.location + protocol_sep.length);
		domainRange.length = [domain length] - domainRange.location;
		domain = [domain substringWithRange: domainRange];
	}
	NSRange firstSlash = [domain rangeOfString: @"/"];
	if(firstSlash.length > 0){
		domainRange.location = 0;
		domainRange.length = firstSlash.location;
		domain = [domain substringWithRange: domainRange];
	}
	domain = [self truncateString: domain toMaxLength: 42];
	return domain;
}

- (NSString *) truncateString: (NSString *)str toMaxLength: (int) len {
	if([str length] < len) {
		return str;
	}
	NSRange range;
	range.location = 0;
	range.length = len - 2;
	str = [[str substringWithRange: range] stringByAppendingString: @"..."];
	return str;
}

- (void) dealloc {
	[source_db release];
	[original_id release];
	[google_id release];
	[date release];
	[url release];
	[title release];
	[content release];
	[feed_name release];
	[tag_name release];
	[super dealloc];
}

- (NSString *) descriptionText {
	return [self dateStr:NO];
}


- (NSString *) dateStr:(BOOL) longFormat {
	NSDate * now = [NSDate date];
	NSDate * then;
	NSString * dateStr;
	NSDateFormatter *timestampReader = [[[NSDateFormatter alloc] init] autorelease];
	[timestampReader setDateFormat: @"yyyyMMddHHmmss"];
	then = [timestampReader dateFromString: date];
	NSTimeInterval timePassed = [now timeIntervalSinceDate:then];
	// bah.. nstimeinterval is just a float of the number of seconds!
	int hours = timePassed / (60 * 60);
	int days = hours / 24;
	NSString * pastOrFuture;
	if(!longFormat) {
		pastOrFuture = @"";
	} else {
		pastOrFuture = (hours < 0) ? _lang(@"in the future","") : _lang(@"ago", "as in, \"7 hours ago\"");
	}
	NSString * hour_s = _lang(@"hour","");
	NSString * hours_s = _lang(@"hours","");
	NSString * day_s = _lang(@"day","");
	NSString * days_s = _lang(@"days","");
	
	if(abs(days) < 1){
		dateStr = [NSString stringWithFormat: @"%d %@ %@", hours, PLURAL(hours, hour_s, hours_s), pastOrFuture];
	} else {
		dateStr = [NSString stringWithFormat: @"%d %@ %@", days, PLURAL(days, day_s, days_s), pastOrFuture];
	}
	return dateStr;
}

- (NSString *) htmlForPosition:(NSString *)position_info {
	NSString * in_s = _lang(@"in", "as in, \"posted 7 hours ago _in_ this feed name\"");
	return [[NSString stringWithFormat:
		@"<html>                                                                                            \n\
			<head>                                                                                          \n\
				<meta name='viewport' content='width=580' />                                                \n\
				<link rel='stylesheet' href='template/style.css' type='text/css' />                         \n\
			</head>                                                                                         \n\
			<body>                                                                                          \n\
				<div class='post-info header'>                                                              \n\
					<h1 id='title'>                                                                         \n\
						<a href='%@'>%@</a>                                <!-- url, title -->              \n\
					</h1>                                                                                   \n\
					<div class='via'>                                                                       \n\
						%@                                                 <!-- feed_name -->               \n\
						%@                                                 <!-- position_info -->           \n\
					</div>                                                                                  \n\
				</div>                                                                                      \n\
				<div class='content'><p>                                                                    \n\
					%@                                                     <!-- content -->                 \n\
				</div>                                                                                      \n\
				<div class='post-info footer'>                                                              \n\
					<div class='date'>                                                                      \n\
						<b>%@</b> %@ <b>%@</b>                             <!-- date, in_s, tag_name -->    \n\
					</div>                                                                                  \n\
					<div>                                                                                   \n\
						(<i>%@</i>)                                        <!-- domain -->                  \n\
					</div>                                                                                  \n\
				</div>                                                                                      \n\
			</body>                                                                                         \n\
		</html>",
		url, title,
		[self truncateString: feed_name toMaxLength: 84],
		position_info,
		content,
		[self dateStr:YES], in_s, tag_name,
		[self domainName]] autorelease];
}

- (void) userDidScrollPast {
	if(sticky_read_state == NO && is_read == NO){
		is_read = YES;
		is_dirty = YES;
		[self save];
	}
}

- (BOOL) userHasMarkedAsUnread {
	return sticky_read_state && !is_read;
}

- (NSString *) ipaper_url { return ipaper_url; }

- (void) setIpaperURL: (NSString *) linkUrl {
	is_dirty = YES;
	NSString * new_string;

	// ensure the url dividing character does not appear unescaped in the URL:
	linkUrl = [linkUrl stringByReplacingOccurrencesOfString:@"|" withString: @"%7C"];
	if([ipaper_url length] > 0) {
		new_string = [NSString stringWithFormat: @"%@|%@", ipaper_url, linkUrl];
	} else {
		new_string = linkUrl;
	}
	
	[ipaper_url release];
	ipaper_url = [new_string retain];
	[self save];
}

- (void) setReadState: (BOOL) read {
	is_read = read;
	sticky_read_state = YES;
	is_dirty = YES;
	[self save];
}

- (BOOL) toggleReadState {
	if (!sticky_read_state) {
		// the first "toggle" saves it - ie mark as UNread
		[self setReadState: NO];
	} else {
		[self setReadState: !is_read];
	}
	return [self userHasMarkedAsUnread];
}

- (BOOL) toggleStarredState {
	is_starred = !is_starred;
	is_dirty = YES;
	[self save];
	return is_starred;
}

- (BOOL) toggleSharedState {
	is_shared = !is_shared;
	is_dirty = YES;
	[self save];
	return is_shared;
}

@end
