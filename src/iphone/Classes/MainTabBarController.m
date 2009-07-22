#import "MainTabBarController.h"
#import "TCHelpers.h"

@implementation MainTabBarController
@synthesize navController;

- (void) activate {
	isActive = YES;
	[self setListScrollToTop:YES];
	[[self itemList] redraw];
}

- (id) itemList {
	return [navController topViewController];
}

-(BOOL) itemListIsActive{
	return [self selectedIndex] == 0;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
	if(interfaceOrientation == UIInterfaceOrientationPortraitUpsideDown) return NO;
	return ![[[[UIApplication sharedApplication] delegate] settings] rotationLock];
}

- (UIView *) rotatingFooterView {
	return nil;
}

- (void) didRotateFromInterfaceOrientation:(UIInterfaceOrientation)previousOrientation {
	for (id notify in rotationNotificationReceivers) {
		[notify didRotateFromInterfaceOrientation: previousOrientation];
	}
}

- (void) setListScrollToTop:(BOOL) doScroll {
	dbg_s(@"scrolling list view to top? %s -- %@", doScroll ? "YES" : "NO", [[navController topViewController] listView]);
	[[[navController topViewController] listView] setScrollsToTop:doScroll];
}

- (void) deactivate {
	[self setListScrollToTop:NO];
	isActive = NO;
}

- (void) addInterestedView:(id) view {
	if(rotationNotificationReceivers == nil) rotationNotificationReceivers = [[NSMutableArray alloc] init];
	[rotationNotificationReceivers addObject: view];
}

- (void) dealloc {
	if(rotationNotificationReceivers != nil) [rotationNotificationReceivers release];
	[super dealloc];
}

@end
