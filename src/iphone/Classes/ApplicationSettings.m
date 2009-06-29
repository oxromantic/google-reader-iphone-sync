#import "ApplicationSettings.h"
#import "TCHelpers.h"

NSString * _docsPath = nil;

NSInteger URL_SAVE_OFFSET = 390;

// these keys should not be changed without good reason - it'll break
// configs saved with an earlier version of the app:
NSString * keyIpaperUser = @"ipaperUser";
NSString * keyIpaperPassword = @"ipaperPassword";
NSString * keyPassword = @"password";
NSString * keyUser = @"user";
NSString * keyNumItems = @"num_items";
NSString * keyTagList = @"tagList";
NSString * keyLastItemID = @"lastItemID";
NSString * keyLastItemTag = @"lastItemTag";
NSString * keyNavBarOnTop = @"navBarOnTop";
NSString * keyRotationLock = @"rotationLock";
NSString * keyOpenLinksIn = @"openLinksIn";
NSString * keyShowReadItems = @"showReadItems";
NSString * keyNewestFirst = @"newestFirst";
NSString * keyMarkAsReadWhenGoingBackwards = @"markAsReadWhenGoingBackwards";

NSString * openLinksInAskMeValue = @"ask";
NSString * openLinksInSafariValue = @"safari";
NSString * openLinksInGrisValue = @"gris";
NSString * openLinksInInstapaperValue = @"instapaper"; //TODO: migrate
NSArray * openLinksInSegmentValues;

NSString * keyUrlSaveService = @"urlSaveService";
NSString * urlSaveInstapaperValue = @"instapaper";
NSString * urlSavePageFeedvalue = @"pagefeed";
NSArray * urlSaveServiceSegmentValues;

NSArray * deprecatedProperties;

@implementation ApplicationSettings
- (NSString *) docsPath {
	docsPath = [ApplicationSettings docsPath];
	return docsPath;
}

+ (NSString *) docsPath {
	if(_docsPath != nil) {
		return _docsPath;
	}
	NSString * testingPath;
	NSFileManager * fileManager = [NSFileManager defaultManager];
	NSString * path = nil;
	
	NSArray * here_path = [[NSString stringWithCString: __FILE__ encoding: NSASCIIStringEncoding] pathComponents];  // path to this file
	NSArray * base_code_path = [here_path subarrayWithRange: NSMakeRange(0, [here_path count] - 3)];                // minus file, and then up 2 directories

	NSArray * paths = [NSArray arrayWithObjects:
		[NSString stringWithFormat: @"/var/%@/GRiS", NSUserName()],     // iPhone
		[NSString stringWithFormat: @"/Users/%@/.GRiS", NSUserName()],  // simulator (in home directory)
		// (we can't use ~/.GRiS because the simulator puts ~ somewhere deep within the simulated filesystem
		[base_code_path componentsJoinedByString: @"/"],                // simulator (inside the code package - no setup required)
		nil];

	int i;
	BOOL isDir;
	for(i=0; i<[paths count]; i++) {
		testingPath = [paths objectAtIndex:i];
		if([fileManager fileExistsAtPath:testingPath isDirectory:&isDir] && isDir && [fileManager isWritableFileAtPath: testingPath]) {
			path = testingPath;
			break;
		}
	}
	
	if(path == nil) {
		// this is the last resort, when none of the above paths exist
		dbg(@"creating a new docs directory in the standard app doc directory");
		path = [[NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) objectAtIndex:0] stringByAppendingPathComponent: @"GRiS"];
		[TCHelpers ensureDirectoryExists: path];
	}
	_docsPath = [path retain];
	return _docsPath;
}

- (void) save {
	[self saveLastViewedItem];
	BOOL success = [plistData writeToFile:[docsPath stringByAppendingPathComponent: plistName] atomically:YES];
	if(!success) {
		NSLog(@"FAILED saving plist");
	} else {
		dbg_s(@"saved data: %@ to file: %@", plistData, [docsPath stringByAppendingPathComponent: plistName]);
	}
}

- (void) load {
	dbg(@"loading plist data from path: %@", [docsPath stringByAppendingPathComponent: plistName]);
	plistData = [[NSMutableDictionary dictionaryWithContentsOfFile:[docsPath stringByAppendingPathComponent: plistName]] retain];
	if(!plistData) {
		NSLog(@"FAILED loading plist");
		plistData = [[NSMutableDictionary dictionary] retain];
	}
	dbg(@"Loaded plist data", plistData);
	dbg_s(@"%@", plistData);
	[self removeDeprecatedProperties];
	[self loadFeedList];
}

- (void) removeDeprecatedProperties {
	for(NSString * deprecatedProperty in deprecatedProperties) {
		[plistData removeObjectForKey: deprecatedProperty];
	}
}

- (void) reloadFeedList {
	[self loadFeedList];
	[self setUIElements];
}

- (NSArray *) loadFeedList {
	NSString * contents = [NSString stringWithContentsOfFile: [docsPath stringByAppendingPathComponent: @"tag_list"] encoding:NSUTF8StringEncoding error:nil];
	id result;
	if(!contents) {
		dbg(@"no feed list loaded");
		result = nil;
	} else {
		NSArray * originalList = [contents componentsSeparatedByString:@"\n"];
		NSMutableArray * feedList = [NSMutableArray arrayWithCapacity: [originalList count]];
		for(NSString * feed in originalList) {
			NSString * trimmedFeed = [feed stringByTrimmingCharactersInSet: [NSCharacterSet whitespaceAndNewlineCharacterSet]];
			if([feed length] > 0) {
				[feedList addObject: trimmedFeed];
			}
		}
		result = feedList;
	}
	[possibleTags release];
	possibleTags = [result retain];
	return result;
}
- (NSArray *) feedList {
	return possibleTags;
}

- (NSArray *) activeTagList {
	// the interestection of "selected" tags with the set of tags that exist according to google reader
	id tags = [self tagList];
	NSArray * result = [NSMutableArray arrayWithCapacity:[tags count]];
	for (NSString * tag in tags) {
		if([possibleTags containsObject: tag]) {
			[result addObject: tag];
		}
	}
	return result;
}


- (id) init {
	self = [super init];
	plistName = @"config.plist";
	if(openLinksInSegmentValues == nil) openLinksInSegmentValues = [[NSArray alloc] initWithObjects: openLinksInAskMeValue, openLinksInSafariValue, openLinksInGrisValue, openLinksInInstapaperValue, nil];
	if(urlSaveServiceSegmentValues == nil) urlSaveServiceSegmentValues = [[NSArray alloc] initWithObjects: urlSaveInstapaperValue, urlSavePageFeedvalue, nil];
	if(deprecatedProperties == nil) deprecatedProperties = [[NSArray alloc] initWithObjects: @"openInSafari", nil];

	[self docsPath];
	[self load];
	return self;
}

- (void) awakeFromNib {
	[smallText setFont: [UIFont systemFontOfSize: 14.0]];
	[self setUIElements];
	[super awakeFromNib];
}

- (void) dealloc {
	dbg(@"settings is being dealloc'd - saving plist data.");
	[self save];
	[plistData release];
	[plistName release];
	[super dealloc];
}

#pragma mark UI actions


- (id) nextInputAfter:(id) sender {
	if(sender == emailField) {
		return passwordField;
	} else if (sender == ipaperEmailField) {
		return ipaperPasswordField;
	}
	return nil;
}

- (BOOL) textFieldShouldReturn:(UITextField *)sender{
	[sender resignFirstResponder];
	id nextInput = [self nextInputAfter:sender];
	if(nextInput) {
		[nextInput becomeFirstResponder];
	}
	return YES;
}

- (IBAction) activatePasswordField:(id)sender {
	[passwordField becomeFirstResponder];
}
- (IBAction) deactivateBothFields:(id)sender {
	[passwordField resignFirstResponder];
	[emailField resignFirstResponder];
	[ipaperEmailField resignFirstResponder];
	[ipaperPasswordField resignFirstResponder];
}

- (BOOL) getNavItem:(id *)navItem andDoneButton:(id*)btn forTextField:(id)sender {
	*btn = nil;
	*navItem = nil;
	if (sender == emailField || sender == passwordField || sender == ipaperEmailField || sender == ipaperPasswordField) {
		*btn = stopEditingAccountButton;
		*navItem = accountNavItem;
	} else {
		dbg(@"unknown sender:%@", sender);
	}
	
	return (*navItem && *btn);
}

- (int) getOffsetForTextFieldEditing: (id) field {
	if(field == ipaperEmailField || field == ipaperPasswordField) {
		return URL_SAVE_OFFSET;
	} else {
		return -1;
	}
}


- (void) setUIElements {
	[emailField setText: [self email]];
	[passwordField setText: [self password]];
	[ipaperEmailField setText: [self ipaperEmail]];
	[ipaperPasswordField setText: [self ipaperPassword]];
	[itemsPerFeedSlider setValue:[self itemsPerFeed]];
	[itemsPerFeedLabel setText:[NSString stringWithFormat:@"%d", [self itemsPerFeed]]];
	[showReadItemsToggle setOn: [self showReadItems]];
	[navBarOnTopToggle setOn: [self navBarOnTop]];
	[openLinksInSegmentControl setSelectedSegmentIndex: [self openLinksInSelectedIndex]];
	[urlSaveServiceSegmentControl setSelectedSegmentIndex: [self urlSaveServiceSelectedIndex]];
	[newestItemsFirstToggle setOn: [self sortNewestItemsFirst]];
	[rotationLockToggle setOn: [self rotationLock]];
	[feedList setSelectedFeeds: [self tagList]];
	[feedList setFeedList: possibleTags];
	for(id view in [feedsPlaceholderView subviews]) {
		[view removeFromSuperview];
	}
	id subview = possibleTags ? feedSelectionView : noFeedsView;
	[feedsPlaceholderView insertSubview: subview atIndex:0];
	CGSize frameSize = [feedsPlaceholderView bounds].size;
	CGRect frame = CGRectMake(0,0, frameSize.width, frameSize.height);
	[subview setFrame: frame];
}

#pragma mark GETTING values
- (int) itemsPerFeedValue: (UISlider *) sender {
	float raw_val = [sender value];
	return (int)(roundf(raw_val / 5)) * 5; // round to the nearest multiple of 5
}

- (BOOL) boolFromKey:(NSString *) key {
	NSNumber * val = [plistData valueForKey:key];
	return val && [val boolValue];
}

- (BOOL) navBarOnTop       { return [self boolFromKey:keyNavBarOnTop]; }
- (BOOL) showReadItems     { return [self boolFromKey:keyShowReadItems]; }
- (BOOL) sortNewestItemsFirst{ return [self boolFromKey:keyNewestFirst]; }
- (BOOL) rotationLock      { return [self boolFromKey:keyRotationLock]; }
- (NSString *) ipaperEmail       { return [plistData valueForKey:keyIpaperUser]; }
- (NSString *) ipaperPassword    { return [plistData valueForKey:keyIpaperPassword]; }

- (BOOL) missingInstapaperDetails {
	BOOL using_ipaper = [self urlSaveServiceSelectedIndex] == urlSaveInstapaperIndex;
	BOOL no_user = [[self ipaperEmail] length] == 0;
	dbg(@"no user? %s", no_user ? "yes!": "no...");
	dbg(@"using ipaper? %s", using_ipaper ? "yes!": "no...");
	dbg(@"missing details? %s", using_ipaper && no_user ? "yes!": "no...");
	return using_ipaper && no_user;
}

// meta-properties (possible values of openLinksIn)
- (int) openLinksInSelectedIndex {
	NSString * value = [plistData valueForKey:keyOpenLinksIn];
	NSUInteger index = [openLinksInSegmentValues indexOfObject: value];
	if (index == NSNotFound) {
		index = 0; // default
	}
	return index;
}

- (int) urlSaveServiceSelectedIndex {
	NSString * value = [plistData valueForKey:keyUrlSaveService];
	NSUInteger index = [urlSaveServiceSegmentValues indexOfObject: value];
	if (index == NSNotFound) {
		index = 0; // default
	}
	return index;
}

- (NSString *) email       { return [plistData valueForKey:keyUser]; }
- (NSString *) password    { return [plistData valueForKey:keyPassword]; }

- (id) tagList     { 
	id tags = [plistData valueForKey:keyTagList];
	if([[tags class] isSubclassOfClass: [@"" class]]) { // TODO: why can't I just pass the NSString class object?
		tags = [tags componentsSeparatedByString:@"\n"];
	}
	return tags;
}
- (int) itemsPerFeed     {
	int val = [[plistData valueForKey:keyNumItems] intValue];
	if(val) return val;
	return 20; // default
}

- (NSString *) getLastViewedItem { return [plistData valueForKey:keyLastItemID]; }
- (NSString *) getLastViewedTag { return [plistData valueForKey:keyLastItemTag]; }
- (BOOL) markAsReadWhenGoingBackwards { return [self boolFromKey: keyMarkAsReadWhenGoingBackwards]; }

#pragma mark SETTING values
- (void) saveValue:(id) val forKey:(NSString *) key {
	[plistData setValue:val forKey:key];
	dbg_s(@"setting value %@ for key %@", val, key);
	[self save];
}

- (void) setBool:(BOOL) val forKey:(NSString *) key {
	[self saveValue: [NSNumber numberWithBool: val] forKey:key];
}

- (void) setNavBarOnTop:(BOOL) newVal        { [self setBool:newVal forKey:keyNavBarOnTop];  }
- (void) setReadItems:(BOOL) newVal          { [self setBool:newVal forKey:keyShowReadItems]; }
- (void) setRotationLock:(BOOL) newVal       { [self setBool:newVal forKey:keyRotationLock]; }
- (void) setOpenLinksIn: (NSString *) newVal { [self saveValue: newVal forKey:keyOpenLinksIn]; }
- (void) setUrlSaveService: (NSString *) newVal { [self saveValue: newVal forKey:keyUrlSaveService]; }
- (void) setSortNewestItemsFirst:(BOOL) newVal {
	[self setBool:newVal forKey:keyNewestFirst];
	[[self globalAppDelegate] refreshItemLists];
}

- (void) saveLastViewedItem {
	[plistData setValue:
		[[[UIApplication sharedApplication] delegate] currentItemID]
		forKey:keyLastItemID];
	[plistData setValue:
		[[[[[[[UIApplication sharedApplication] delegate] mainController] navController] topViewController] delegate] tag]
		forKey:keyLastItemTag];
}

- (void) setTagList: (NSArray *) selectedTags {
	[self saveValue:selectedTags forKey:keyTagList];
}

#pragma mark event handlers

- (IBAction) stringValueDidChange:(id)sender {
	NSString * key;
	if(sender == emailField) {
		key = keyUser;
	} else if (sender == passwordField) {
		key = keyPassword;
	} else if (sender == ipaperPasswordField) {
		key = keyIpaperPassword;
	} else if (sender == ipaperEmailField) {
		key = keyIpaperUser;
	} else {
		NSLog(@"unknown item sent ApplicationSettings stringValueDidChange: %@", sender);
		return;
	}
	[self saveValue: [sender text] forKey:key];
}

- (IBAction) switchValueDidChange:(id) sender {
	BOOL newValue = [[sender valueForKey:@"on"] boolValue];
	if(sender == showReadItemsToggle) {
		[self setReadItems: newValue];
	} else if(sender == rotationLockToggle) {
		[self setRotationLock: newValue];
	} else if(sender == newestItemsFirstToggle) {
		[self setSortNewestItemsFirst: newValue];
	} else if(sender == navBarOnTopToggle) {
		[self setNavBarOnTop: newValue];
	} else {
		dbg(@"unknown sender sent switchValueDidChange to ApplicationSettings");
	}
}

- (IBAction) segmentValueDidChange:(id) sender {
	if(sender == openLinksInSegmentControl) {
		[self setOpenLinksIn: [openLinksInSegmentValues objectAtIndex: [sender selectedSegmentIndex]]];
	} else if(sender == urlSaveServiceSegmentControl) {
		[self setUrlSaveService: [urlSaveServiceSegmentValues objectAtIndex: [sender selectedSegmentIndex]]];
	} else {
		dbg(@"unknown sender to segmentValueDidChange: %@", sender);
	}
}

// general handler for text view & text fields
- (void) textElementDidFinishEditing:(id) sender {
	[sender resignFirstResponder];

	// hide any done buttons if necessary)
	id btn = nil;
	id navItem = nil;
	if([self getNavItem:&navItem andDoneButton:&btn forTextField:sender]) {
		[navItem setRightBarButtonItem: nil];
	}
	[self stringValueDidChange:sender];
}

- (IBAction) textElementDidBeginEditing:(UITextField *)sender {
	id btn = nil;
	id navItem = nil;
	int scrollOffset;
	if([self getNavItem:&navItem andDoneButton:&btn forTextField:sender]) {
		[navItem setRightBarButtonItem: btn];
	}
	
	scrollOffset = [self getOffsetForTextFieldEditing:sender];
	if(scrollOffset != -1) {
		dbg(@"Scrolling to: %d", scrollOffset);
		[mainScrollView setContentOffset: CGPointMake(0, scrollOffset) animated:YES];
	}
}

// begin editing
- (IBAction) textFieldDidBeginEditing:(UITextField *)sender { [self textElementDidBeginEditing:sender]; }
- (IBAction) textViewDidBeginEditing: (UITextField *)sender { [self textElementDidBeginEditing:sender]; }

// end editing
- (IBAction) textFieldDidEndEditing:(UITextField *)sender { [self textElementDidFinishEditing:sender]; }
- (IBAction) textViewDidEndEditing: (UITextField *)sender { [self textElementDidFinishEditing:sender]; }


// handle the slider when it, er, slides...
- (IBAction) itemsPerFeedDidChange: (id) sender {
	int itemsPerFeed = [self itemsPerFeedValue: sender];
	[itemsPerFeedLabel setText: [NSString stringWithFormat: @"%d", itemsPerFeed]];
	[self saveValue:[NSNumber numberWithInt:itemsPerFeed] forKey:keyNumItems];
	[sender setValue: itemsPerFeed];
}

// TODO: hook up a "clear instapaper" button

@end
