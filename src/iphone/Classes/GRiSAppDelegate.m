#import "GRiSAppDelegate.h"
#import "ItemView.h"
#import "TCHelpers.h"

@implementation GRiSAppDelegate

- (void) applicationWillTerminate:(id) sender {
	dbg(@"terminating...");
	[syncController cancelSync:self];
	[appSettings dealloc];
	[db dealloc];
}

- (void) applicationDidReceiveMemoryWarning: (id) app {
	dbg(@"WARNING: out of memory warning received. GRiS will probably die horribly.");
}

- (BOOL) inItemViewMode { return inItemViewMode; }
- (id) settings { return appSettings; }
- (id) mainController { return mainController; }

- (void)applicationDidFinishLaunching:(UIApplication *)application {
	[syncController ensureSingleton];
	[window setBackgroundColor: [UIColor groupTableViewBackgroundColor]];
	
	loading = YES;
	[self loadFirstView];
}

- (void) loadItemAtIndex: (int) index fromSet:(id) items {
	[[browseController webView] loadItemAtIndex: index fromSet:items];
	[self showViewer:self];
}

- (void)showNavigation: (id) sender {
	[self refreshItemLists];
	[[browseController webView] showCurrentItemInItemList: [mainController itemList]];
	[browseController deactivate];
	[self setViewToShowItem: NO];
	[mainController activate];
}

- (void) removeBrowseView {
	[[browseController view] removeFromSuperview];
}

- (void) setViewToShowItem:(BOOL) showItemView {
	BOOL withAnimation = !loading;
	inItemViewMode = showItemView;
	
	// tab / navigation bar:
	[[mainController tabBar] setHidden: showItemView];
	
	id viewController = [mainController selectedViewController];
	if([viewController respondsToSelector: @selector(navigationBar)]) {
		[[viewController navigationBar] setHidden: showItemView];
	}
	
	// viewer
	if(showItemView) {
		[[mainController view] addSubview:[browseController view]];
		[[browseController view] fitToSuperview];
		[[browseController view] setHidden:NO];
	} else {
		[self removeBrowseView];
	}
	[[mainController view] layoutSubviews];
}

- (void)showViewer: (id) sender {
	[mainController deactivate];
	[self setViewToShowItem: YES];
	[browseController activate];
}

- (void) refreshItemLists {
	for(id controller in [[mainController navController] viewControllers]) {
		[controller refresh:self];
	}
	[feedList reloadData];
}

- (IBAction) toggleOptions: (id) sender {
	id optionsButton = [[[[mainController navController] topViewController] navigationItem] rightBarButtonItem];
	UIView * currentView = [[[[mainController navController] topViewController] view] superview];
	id subviews = [currentView subviews];
	if([subviews containsObject: optionsView]) {
		[optionsUnderlayView removeFromSuperview];
		[optionsView removeFromSuperview];
		[self refreshItemLists];
		[optionsButton setTitle: _lang(@"Options","")];
	} else {
		[currentView addSubview: optionsUnderlayView];
		[optionsUnderlayView fitToSuperview];
		[currentView addSubview: optionsView];
		[optionsView fitToSuperviewWidth];
		[optionsView setHidden: NO];
		[optionsView animateFadeIn];
		[optionsButton setTitle: _lang(@"Done","")];
	}
}
- (id) currentListController {
	return [[mainController navController] topViewController];
}
- (IBAction) markItemsAsRead: (id) sender    { [self markItemsWithReadState: YES]; }
- (IBAction) markItemsAsUnread: (id) sender  { [self markItemsWithReadState: NO];  }

- (void) markItemsWithReadState: (BOOL) read {
	[[self currentListController] markItemsWithReadState:read];
	[self toggleOptions: self];
}
	
- (void) loadFirstView {
	NSString * itemID = [appSettings getLastViewedItem];
	NSString * tag = [appSettings getLastViewedTag];
	[self showNavigation: self];
	if(!(itemID == nil || [itemID length] == 0 || tag == nil || [tag length] == 0)) {
		dbg(@"loading tag %@, item %@", tag, itemID);
		[itemListDelegate loadItemWithID:itemID fromTag: tag];
	}
	[window addSubview:[mainController view]];
	loading = NO;
}

- (NSString *) currentItemID {
	NSString * itemID = nil;
	if(inItemViewMode) {
		itemID = [browseController currentItemID];
	}
	return itemID;
}

@end

