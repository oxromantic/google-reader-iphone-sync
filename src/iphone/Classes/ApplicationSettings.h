#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

enum {
	openLinksInAskMeIndex = 0
	, openLinksInSafariIndex = 1
	, openLinksInGrisIndex = 2
	, openLinksInInstapaperIndex = 3
} openLinksIndexEnum;

enum {
	urlSaveInstapaperIndex = 0
	, urlSavePageFeedIndex = 1
} urlSaveIndexEnum;

@interface ApplicationSettings : NSObject {
	NSString * docsPath;
	NSMutableDictionary * plistData;
	NSString * plistName;
	
	NSArray * possibleTags;
	
	IBOutlet id emailField;
	IBOutlet id passwordField;
	IBOutlet id ipaperEmailField;
	IBOutlet id ipaperPasswordField;

	IBOutlet id tagListField;
	IBOutlet id itemsPerFeedSlider;
	IBOutlet id itemsPerFeedLabel;
	
	IBOutlet id tagListNavItem;
	IBOutlet id stopEditingFeedsButton;

	IBOutlet id accountNavItem;
	IBOutlet id stopEditingAccountButton;
	
	IBOutlet id showReadItemsToggle;
	IBOutlet id rotationLockToggle;
	IBOutlet id navBarOnTopToggle;
	IBOutlet id markAsReadWhenGoingBackwardsToggle;
	IBOutlet id newestItemsFirstToggle;
	IBOutlet id openLinksInSegmentControl;
	BOOL rotationLock;
	
	IBOutlet id urlSaveServiceSegmentControl;
	IBOutlet id urlSaveInstapaperView;
	IBOutlet id urlSavePageFeedView;
	UIView * urlSaveView;
	IBOutlet UIView * urlSaveViewContainer;
	
	IBOutlet id feedList;
	IBOutlet id noFeedsView;
	IBOutlet id feedSelectionView;
	IBOutlet id feedsPlaceholderView;
	
	IBOutlet id smallText;
	IBOutlet id mainScrollView;
	IBOutlet id helpView;
	IBOutlet id mainContentView;
}
-(NSString *) docsPath;
-(NSString *) email;
-(NSString *) password;
-(int) itemsPerFeed;

- (IBAction) itemsPerFeedDidChange: (id) sender;
- (IBAction) stringValueDidChange:(id)sender;
- (IBAction) switchValueDidChange:(id) sender;
- (IBAction) segmentValueDidChange:(id) sender;

- (IBAction) showHelp:(id) sender;
- (IBAction) hideHelp:(id) sender;

- (IBAction) activatePasswordField:(id)sender;
- (IBAction) deactivateBothFields:(id)sender;
- (IBAction) textFieldDidEndEditing:(UITextField *)sender;
- (IBAction) deactivateTagListField:(id) sender;
- (IBAction) launchPageFeedUrl:(id) sender;
- (BOOL) markAsReadWhenGoingBackwards;
- (int) openLinksInSelectedIndex;

@end
