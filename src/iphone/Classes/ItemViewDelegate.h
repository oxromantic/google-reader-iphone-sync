#import <UIKit/UIKit.h>
#import "ItemView.h"

@interface ItemViewDelegate : NSObject {
	IBOutlet id spinner;
	id waitingForInstapaperLinkClick;
	NSURLRequest * pendingRequest;
	IBOutlet UIWebView * webView;
	IBOutlet UIView * viewerView;
	IBOutlet ItemView * itemView;
}

@end
