#import "TagItem.h"
#import "TCHelpers.h"


@implementation TagItem

- (id) initWithTag: (NSString *) _tag count:(int) _count db:(id) _db {
	self = [super init];
	tag = [_tag retain];
	db = [_db retain];
	count = _count;
	return self;
}

- (BOOL) hasChildren { return YES; }
- (BOOL) is_starred { return NO; }
- (BOOL) is_read    { return NO; }
- (BOOL) count      { return count; }

- (NSString *) tagValue {
	return tag;
}

- (NSString *) descriptionText {
	if(count < 0) return @"";
	NSString * item_s = _lang(@"item","");
	NSString * items_s = _lang(@"items","");
	return [NSString stringWithFormat: @"%d %@", count, PLURAL(count, item_s, items_s)];
}

- (void) refreshCount {
	count = [db itemCountForTag:tag];
}

- (NSString *) title {
	return tag;
}

- (void) dealloc {
	[tag release];
	[db release];
}

@end
