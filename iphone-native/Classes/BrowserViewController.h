#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface BrowserViewController : UIViewController {
	IBOutlet id webViewContainer;
	IBOutlet UIView * webView;
	IBOutlet UIView * navigationView;
	IBOutlet UIView * browseScreenView;
	IBOutlet id topLevelWindow;
}
- (void) activate;
- (void) deactivate;
@end
