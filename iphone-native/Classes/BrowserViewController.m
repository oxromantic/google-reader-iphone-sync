#import "BrowserViewController.h"
#import "TCHelpers.h"
#import "ApplicationSettings.h"

@implementation BrowserViewController
- (id) webView { return webView; }

- (id) currentItemID {
	return [webView currentItemID];
}

- (void) activate {
	ApplicationSettings * settings = [[[UIApplication sharedApplication] delegate] settings];

	// position the navigation bar appropriately
	int navHeight = [navigationView bounds].size.height;
	CGRect webViewFrame = [webViewContainer frame];
	CGRect navViewFrame = [navigationView frame];
	UIViewAutoresizing resizeMask;

	if([settings navBarOnTop]) {
		// webViewFrame.origin.y = 0;
		navViewFrame.origin.y = 0;
		resizeMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin;
	} else {
		// webViewFrame.origin.y = 0;
		navViewFrame.origin.y = webViewFrame.size.height - navViewFrame.size.height;
		resizeMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
	}
	[webViewContainer setFrame: webViewFrame];
	[navigationView setFrame: navViewFrame];
	[navigationView setAutoresizingMask: resizeMask];
	
	// set opacity
	[navigationView setAlpha: [settings navBarOpacity]];

	// now load the actual content
	[webView load];
}

- (void) deactivate {
	[webView deactivate];
}

@end
