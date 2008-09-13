#import <UIKit/UIKit.h>
#import "browserViewController.h"
#import "MainTabBarController.h"

@interface GRiSAppDelegate : NSObject {
	IBOutlet UIWindow *window;
	IBOutlet id db;
	IBOutlet BrowserViewController * browseController;
	IBOutlet MainTabBarController * mainController;
	IBOutlet id appSettings;
	IBOutlet id itemListDelegate;

	IBOutlet id optionsView;
	BOOL inItemViewMode;
}

@property (nonatomic, retain) UIWindow *window;

- (IBAction) toggleOptions: (id) sender;
- (IBAction) showNavigation: (id) sender;
- (IBAction) showViewer: (id) sender;
- (NSString *) appDocsPath;
- (id) settings;
- (IBAction) markItemsAsRead: (id) sender;
- (IBAction) markItemsAsUnread: (id) sender;
@end