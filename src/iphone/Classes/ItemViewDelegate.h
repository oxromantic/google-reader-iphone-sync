#import <UIKit/UIKit.h>


@interface ItemViewDelegate : NSObject {
	IBOutlet id spinner;
	id waitingForInstapaperLinkClick;
	NSURLRequest * pendingRequest;
	IBOutlet UIWebView * webView;
	IBOutlet UIView * viewerView;
}

@end
