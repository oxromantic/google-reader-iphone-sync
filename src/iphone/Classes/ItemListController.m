#import "ItemListController.h"
#import "TCHelpers.h"

@implementation ItemListController
- (id) initWithDelegate: (id) _delegate {
	self = [super init];
	[self setDelegate: _delegate];
	return self;
}

- (id) title {
	NSString * title = [delegate tag];
	if(!title) {
		title = [NSString stringWithFormat: @"[%s]", _lang(@"no tag","")];
	}
	return title;
}

- (void) setListView: (id) _listView {
	[_listView retain];
	[listView release];
	listView = _listView;
}

- (void) setDB: (id) db {
	[[self delegate] setDB: db];
	[listView reloadData];
}
- (id) delegate {
	return delegate;
}

- (id) listView { return listView; }

- (void) setDelegate: (id) _delegate {
	[_delegate retain];
	[delegate release];
	delegate = _delegate;
}

- (void) selectItemWithID:(NSString *) google_id {
	id indexPath = [[self delegate] getIndexPathForItemWithID:google_id];
	if(indexPath) {
		[listView selectRowAtIndexPath:indexPath animated:NO scrollPosition:UITableViewScrollPositionTop];
	}
}

- (void) redraw{
	[listView reloadData];
}

-(IBAction) refresh: (id) sender {
	[delegate reloadItems];
	[listView reloadData];
	[self redraw];
	[listView setNeedsDisplay]; // this shouldn't be necessary, surely...
}

- (IBAction) markItemsAsRead:   (id) sender { [self markAllItemsWithReadState: YES]; }
- (IBAction) markItemsAsUnread: (id) sender { [self markAllItemsWithReadState: NO];  }

- (void) markItemsWithReadState: (BOOL) read {
	NSString * read_s = _lang(@"read","");
	NSString * unread_s = _lang(@"unread","");
	alertWasForMarkingAsRead = read;
	markAsReadAlert = [[UIAlertView alloc]
		initWithTitle: [NSString stringWithFormat: _lang(@"Mark as %@",""), read ? read_s : unread_s]
		message: [NSString stringWithFormat: _lang(@"Do you really want to mark all these items as %@?",""), read ? read_s : unread_s]
		delegate: self
		cancelButtonTitle: _lang(@"Cancel","")
		otherButtonTitles: _lang(@"OK",""), nil];
	[markAsReadAlert show];
}

- (void) alertView:(id)_view clickedButtonAtIndex:(NSInteger) index {
	if(index == 1 && _view == markAsReadAlert) {
		[[self delegate] setAllItemsReadState: alertWasForMarkingAsRead];
		[[self delegate] reloadItems];
		[[[UIApplication sharedApplication] delegate] refreshItemLists];
	}
	[_view release];
}

@end
