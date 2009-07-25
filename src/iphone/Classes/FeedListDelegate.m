#import "FeedListDelegate.h"
#import "TCHelpers.h"

@implementation FeedListDelegate
- (void) dealloc {
	[selectedFeedList release];
	[feedList release];
}

- (void) setSelectedFeeds: feeds {
	[selectedFeedList retain];
	selectedFeedList = [[NSMutableArray alloc] initWithArray: feeds];
}

- (void) setFeedList: feeds {
	[feedList release];
	feedList = [[NSMutableArray alloc] initWithArray: feeds];
}

- tableView:(id)view cellForRowAtIndexPath: (id) indexPath {
	UITableViewCell * cell = [view dequeueReusableCellWithIdentifier:@"feedListCell"];
	if(cell == nil) {
		cell = [[UITableViewCell alloc] initWithFrame: CGRectMake(0,0,1,1) reuseIdentifier:@"feedListCell"];
		[cell setSelectionStyle: UITableViewCellSelectionStyleNone];
	}

	UITableViewCell * firstCell = [view dequeueReusableCellWithIdentifier:@"refreshFeedListCell"];
	if(firstCell == nil) {
		firstCell = [[UITableViewCell alloc] initWithFrame: CGRectMake(0,0,1,1) reuseIdentifier:@"refreshFeedListCell"];
		[firstCell setTarget: syncController];
		[firstCell setAccessoryAction: @selector(syncStatusOnly:)];
		[firstCell setAccessoryType: UITableViewCellAccessoryDetailDisclosureButton];
		[firstCell setTextAlignment: UITextAlignmentCenter];
		[firstCell setText: _lang(@"Reload tag list", "")];
		[firstCell setTextColor: [UIColor darkGrayColor]];
		[firstCell setIndentationLevel: 2];
	}

	int index = [self feedIndexForIndexPath:indexPath];
	if(index == -1) {
		return firstCell;
	}
	if(feedList) {
		NSString * feedName = [feedList objectAtIndex: index];
		[cell setText:feedName];
		UIColor * textColor;
		if([selectedFeedList containsObject: feedName]) {
			[cell setAccessoryType: UITableViewCellAccessoryCheckmark];
			textColor = [UIColor blackColor];
		} else {
			[cell setAccessoryType: UITableViewCellAccessoryNone];
			textColor = [UIColor lightGrayColor];
		}
	
		[cell setTextColor: textColor];
	} else {
		[cell setText:@"Unable to get feed list"];
		[cell setAccessoryType: UITableViewCellAccessoryNone];
	}
	return cell;
}

- (int) numberOfSectionsInTableView:(id)view {
	return 1;
}

- (int) feedIndexForIndexPath: (NSIndexPath *) path {
	return [TCHelpers lastIndexInPath:path] - 1;
}

- (void) tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
	int index = [self feedIndexForIndexPath: indexPath];
	if(index < 0) { return; }
	if(feedList) {
		NSString * selectedFeed = [feedList objectAtIndex: index];
		if([selectedFeedList containsObject:selectedFeed]) {
			[selectedFeedList removeObject:selectedFeed];
		} else {
			[selectedFeedList addObject: selectedFeed];
		}
	}
	[tableView reloadData];
	[appSettings setTagList: selectedFeedList];
}

- (int) tableView:(id)view numberOfRowsInSection:(id)section {
	if(!feedList) {
		return 1;
	} else {
		return [feedList count] + 1;
	}
}

@end
