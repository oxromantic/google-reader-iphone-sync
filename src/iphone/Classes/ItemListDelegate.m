#import "ItemListDelegate.h"
#import "ItemListController.h"
#import "ItemSet.h"
#import "TCHelpers.h"
#import "TagItem.h"

@implementation ItemListDelegate
- (id) init {
	return [self initWithTag:nil db:nil];
}

- (id) initWithTag:(NSString *) _tag db:(id)_db {
	self = [super init];
	tag = [_tag retain];
	db = [_db retain];
	return self;
}

- (id) tag {
	return tag;
}


- (id) tableView:(id)view cellForRowAtIndexPath: (id) indexPath {
	id titleLabel, descriptionLabel;
	UITableViewCell * cell = [view dequeueReusableCellWithIdentifier:@"itemCell"];
	if(cell == nil) {
		cell = [[UITableViewCell alloc] initWithFrame: CGRectMake(0,0,1,1) reuseIdentifier:@"itemCell"];
		
		descriptionLabel = [[[UILabel alloc] initWithFrame:CGRectMake(280.0, 12.0, 50.0, 25.0)] autorelease];
		[descriptionLabel setBackgroundColor: [UIColor whiteColor]];
		[descriptionLabel setAdjustsFontSizeToFitWidth: YES];
		[descriptionLabel setMinimumFontSize: 10.0];
		[descriptionLabel setFont: [UIFont systemFontOfSize:13.0]];
		[descriptionLabel setTextAlignment: UITextAlignmentRight];
		[descriptionLabel setTextColor: [UIColor lightGrayColor]];
		[descriptionLabel setAutoresizingMask: UIViewAutoresizingFlexibleRightMargin];
		[cell setAccessoryView:descriptionLabel];
		
		[cell setFont: [UIFont systemFontOfSize:14.0]];
	} else {
		descriptionLabel = (UILabel *)[cell accessoryView];
	}
	
	id item = [self itemAtIndexPath:indexPath];
	[cell setText: [item title]];
	[descriptionLabel setText: [item descriptionText]];
	
	UIColor * textColor = [item is_read] ? [UIColor lightGrayColor] : [UIColor blackColor]; // nil should work (for black), but doesn't
	[cell setTextColor: textColor];
	
	UIImage * image = nil;
	if([item hasChildren]) {
		image = [self folderImage];
	} else {
		if([item is_starred]) {
			image = [item is_shared] ? [self sharedAndStarredImage] : [self starredImage];
		} else {
			image = [item is_shared] ? [self sharedImage] : nil;
		}
	}

	[cell setImage: image];
	
	UITableViewCellSelectionStyle selStyle = [item is_read]? UITableViewCellSelectionStyleGray : UITableViewCellSelectionStyleBlue;
	[cell setSelectionStyle: selStyle];
	
	return cell;
}


- (UIFont *) cellFont {
	if(cellFont == nil) {
		cellFont = [[UIFont systemFontOfSize:16.0] retain];
	}
	return cellFont;
}
		
- (UIImage *) starredImage {
	if(starredImage == nil) {
		starredImage = [UIImage imageNamed: @"emblem_starred.png"];
	}
	return starredImage;
}

- (UIImage *) sharedImage {
	if(sharedImage == nil) {
		sharedImage = [UIImage imageNamed: @"emblem_shared.png"];
	}
	return sharedImage;
}

- (UIImage *) folderImage {
	if(folderImage == nil) {
		folderImage = [UIImage imageNamed: @"emblem_folder.png"];
	}
	return folderImage;
}


- (UIImage *) sharedAndStarredImage {
	if(sharedAndStarredImage == nil) {
		sharedAndStarredImage = [UIImage imageNamed: @"emblem_shared_and_starred.png"];
	}
	return sharedAndStarredImage;
}

- (int)numberOfSectionsInTableView:(id)view {
	return 1;
}

- (id) itemAtIndexPath: (id) indexPath {
	id item = [[self itemSet] objectAtIndex: [self itemIndexFromIndexPath: indexPath]];
	return item;
}

- (NSUInteger) itemIndexFromIndexPath: (id) indexPath {
	NSUInteger index = [indexPath indexAtPosition: [indexPath length] - 1];
	return index;
}

- (id) createControllerForTag: (NSString *) tag {
	ItemListController * newItemListController = [[[ItemListController alloc] init] autorelease];
	ItemListDelegate * newItemDelegate = [[[ItemListDelegate alloc] initWithTag: tag db: db] autorelease];
	UITableView * newTableView = [[[UITableView alloc] init] autorelease];
	
	[newItemListController setDelegate: newItemDelegate];
	[newTableView setDelegate: newItemDelegate];
	[newTableView setDataSource: newItemDelegate];
	[newTableView setAutoresizingMask: UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight];
	[newItemListController setView: newTableView];
	[newItemListController setListView: newTableView];

	// use the current "options" button for all views
	id rightButton = [[[navigationController navigationBar] topItem] rightBarButtonItem];
	[[newItemListController navigationItem] setRightBarButtonItem: rightButton];
	return newItemListController;
}	

- (void) tableView:(id)view didSelectRowAtIndexPath:(id) indexPath {
	int itemIndex = [self itemIndexFromIndexPath:indexPath];
	id item = [[self itemSet] objectAtIndex: itemIndex];
	if([item hasChildren]) {
		ItemListController * newItemListController = [self createControllerForTag: [item tagValue]];
		
		[navigationController pushViewController: newItemListController animated:YES];
	} else {
		// load it
		[[[UIApplication sharedApplication] delegate] loadItemAtIndex: itemIndex fromSet: [self itemSet]];
	}
}

- (void) loadItemWithID:(NSString *) google_id fromTag:(NSString *) _tag {
	if(!_tag) {
		dbg(@"no tag to load item from - returning");
		return;
	}
	if(![_tag isEqualToString:tag]) {
		id tagController = [self createControllerForTag: _tag];
		[navigationController pushViewController: tagController animated:NO];
		[[tagController delegate] loadItemWithID: google_id fromTag: _tag];
		return;
	}
	
	int index;
	id items = [self itemSet];
	id item;
	for(index = 0; index < [items count]; index++) {
		item = [items objectAtIndex:index];
		if([item respondsToSelector:@selector(google_id)] && [[item google_id] isEqualToString: google_id]) {
			[[[UIApplication sharedApplication] delegate] loadItemAtIndex: index fromSet: items];
			return;
		} else {
			dbg(@"item does not match google id: %@ (item = %@)", google_id, item);
		}
	}
}

- (id) getIndexPathForItemWithID:(NSString *) google_id {
	int foundAtIndex = -1;
	int index;
	
	itemSet = [self itemSet];
	int count = [itemSet count];
	for(index = 0; index < count; index++) {
		if([[[itemSet objectAtIndex:index] google_id] isEqualToString: google_id]) {
			// found it!
			foundAtIndex = index;
			break;
		}
	}
	if(foundAtIndex < 0) {
		return nil;
	}
	NSUInteger indexes[2];
	indexes[0] = 0;
	indexes[1] = foundAtIndex;
	return [NSIndexPath indexPathWithIndexes:indexes length:2];
}


- (void) reloadItems {
	[itemSet release];
	itemSet = nil;
}

- (void) setDB:(id) _db {
	[db release];
	db = [db retain];
	[self reloadItems];
}

- (id) itemSet {
	if(!itemSet) {
		itemSet = [[[ItemSet alloc] initWithTag: tag db: db] getItems];
		if(tag == nil && [itemSet count] > 1) {
			// add the "All Items" tag
			itemSet = [NSMutableArray arrayWithArray: itemSet];
			[itemSet insertObject: [[[TagItem alloc] initWithTag: _lang(@"All Items","") count: [db itemCountForTag:nil] db:db] autorelease] atIndex: 0];
		}
		[itemSet retain];
	}
	return itemSet;
}

- (BOOL) reloadTags {
	BOOL didSomething = NO;
	for (id item in [self itemSet]) {
		if([item hasChildren]) {
			[item refreshCount];
			didSomething = YES;
		} else {
			// fail fast so we don't bother checking the rest of the feeds
			// NOTE: this is dodgy if we are to ever have a view with both items and tags. but we don't yet :p
			return NO;
		}
	}
	return didSomething;
}

- (void) navigationController:(id) navController willShowViewController:(id) viewController animated: (BOOL) animated {
	if([[viewController delegate] reloadTags]) {
		[[viewController listView] reloadData];
	}
}

- (void) setAllItemsReadState: (BOOL) readState {
	dbg(@"marking all items as read for tag: %@", tag);
	[db setAllItemsReadState: readState forTag: tag];
}

- (int)tableView:(id)view numberOfRowsInSection:(id)section {
	return [[self itemSet] count];
}

-(void) tableView:(UITableView*)tableView willBeginEditingRowAtIndexPath:(NSIndexPath *)indexPath {
	// the mere presence of this method causes a swipe action to be recognised,
	// and a delete button appears. like magic!
}

-(void) tableView:(UITableView*) tableView titleForDeleteConfirmationButtonForRowAtIndexPath:(NSIndexPath*) path {
	return _lang(@"hide", "");
}

- (UITableViewCellEditingStyle) tableView:(UITableView *)tv editingStyleForRowAtIndexPath:(NSIndexPath *) indexPath {
	id item = [self itemAtIndexPath: indexPath];
	if([item hasChildren] || [item is_read]) {
		return UITableViewCellEditingStyleNone;
	}
	return UITableViewCellEditingStyleDelete;
}

- (void) tableView:(UITableView *)tv commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath {
	if (editingStyle == UITableViewCellEditingStyleDelete) {
		// delete the item
		id item = [self itemAtIndexPath: indexPath];
		[item setReadState: YES];
		[self reloadItems];
		id settings = [[[UIApplication sharedApplication] delegate] settings];
		if(![settings showReadItems]) {
			[tv deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationFade];
		} else {
			[tv reloadData];
		}
    }
}

- (void) dealloc {
	dbg(@"dealloc: %@", self);
	[starredImage release];
	[folderImage release];
	[sharedImage release];
	[sharedAndStarredImage release];
	[itemSet release];
	[cellFont release];
	[db release];
	[super dealloc];
}

@end

