#import "ItemViewDelegate.h"
#import "TCHelpers.h"


@implementation ItemViewDelegate

- (void) init {
	self = [super init];
	if(!self) return nil;
	[self clearInstapaperWait];
	return self;
}

- (void) clearInstapaperWait {
	waitingForInstapaperLinkClick = nil;
}

- (BOOL) webView:(id) view shouldStartLoadWithRequest:(NSURLRequest *) request navigationType:(UIWebViewNavigationType) type
{
	bool dealtWith = NO;
	if(type == UIWebViewNavigationTypeLinkClicked) {
		if(waitingForInstapaperLinkClick) {
			dbg(@"saving url for instapaper: %@", [[request URL] absoluteString]);
			[waitingForInstapaperLinkClick setIpaperURL: [[request URL] absoluteString]];
			dealtWith = YES;
		}
		waitingForInstapaperLinkClick = nil;
		if (dealtWith) return NO;
		
		if([[self globalAppSettings] openLinksInSafari]) {
			dbg(@"opening url in safari: %@", [request URL]);
			[[self globalApp] openURL: [request URL]];
			return NO;
		}
	}
	return YES;
}

- (void) showSpinner:(BOOL) doShow {
	[spinner setHidden: !doShow];
	doShow ? [spinner startAnimating] : [spinner stopAnimating];
}

- (void) webViewDidStartLoad:(id) sender {
	[self clearInstapaperWait];
	[self showSpinner: YES];
}

- (void) webViewDidFinishLoad:(id) sender {
	[self showSpinner:NO];
}

- (void) setWaitingForInstapaperLinkClick: (id) sender {
	waitingForInstapaperLinkClick = sender;
}

@end
