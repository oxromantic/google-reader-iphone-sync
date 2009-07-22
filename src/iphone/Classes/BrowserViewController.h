#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface BrowserViewController : UIViewController {
	IBOutlet id webViewContainer;
	IBOutlet id webView;
	IBOutlet id navigationView;
	IBOutlet id browseScreenView;
}
- (void) activate;
- (void) deactivate;
@end
