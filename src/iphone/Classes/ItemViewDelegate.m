#import "ItemViewDelegate.h"
#import "ApplicationSettings.h"
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

- (IBAction) actionSheet: (id) sender clickedButtonAtIndex: (NSInteger) index {
	dbg(@"clicked %d", index);
	switch(index) {
		case 0: [self openInSafari: pendingRequest];     break;
		case 1: [self forceOpenInGris: pendingRequest];  break;
		case 2: [self saveToInstapaper: pendingRequest]; break;
	}
}

- (void) openInSafari:(NSURLRequest *) req {
	[[self globalApp] openURL: [req URL]];
	[self clearPendingRequest];
}

- (void) saveToInstapaper:(NSURLRequest *) req {
	dbg(@"saving url for instapaper: %@", [[req URL] absoluteString]);
	[waitingForInstapaperLinkClick setIpaperURL: [[req URL] absoluteString]];
	waitingForInstapaperLinkClick = nil;
	[TCHelpers alertCalled:@"Instapaper" saying:_lang(@"Link will be saved on next sync.","")];
	[self clearPendingRequest];
}

- (void) clearPendingRequest {
	[pendingRequest release];
	pendingRequest = nil;
}

- (void) forceOpenInGris:(NSURLRequest *) res {
	[webView loadRequest: pendingRequest];
	[self clearPendingRequest];
}

- (void) promptForWhereToOpenLink: (NSURLRequest *) req {
	dbg(@"asking...");
	NSString * open_here = _lang(@"open here","");
	NSString * read_later = _lang(@"read later","");
	pendingRequest = [req retain];
	UIActionSheet * actionSheet = [[[UIActionSheet alloc] initWithTitle:_lang(@"Open link with:","")
		delegate: self
		cancelButtonTitle: _lang(@"Cancel","")
		destructiveButtonTitle: nil
		otherButtonTitles:
			_lang(@"Safari",""),
			[NSString stringWithFormat: @"GRiS (%@)", open_here],
			[NSString stringWithFormat: @"Instapaper (%@)", read_later],
			nil] autorelease];
	[actionSheet showInView: viewerView];
}

- (BOOL) webView:(id) view shouldStartLoadWithRequest:(NSURLRequest *) request navigationType:(UIWebViewNavigationType) type
{
	if(type == UIWebViewNavigationTypeLinkClicked) {
		if(waitingForInstapaperLinkClick) {
			[self saveToInstapaper: request];
			return NO;
		}
		
		if (pendingRequest != nil) {
			return YES;
		}
		
		switch((int)([[self globalAppSettings] openLinksInSelectedIndex])) {
			case openLinksInAskMeIndex:
				[self promptForWhereToOpenLink: request];
				return NO;
			break;
			
			case openLinksInSafariIndex:
				[self openInSafari: request];
				return NO;
			break;
			
			case openLinksInGrisIndex:
				return YES;
			break;
			
			case openLinksInInstapaperIndex:
				[self saveToInstapaper:request];
				return NO;
			break;
			
			default: dbg(@"unknown \"open with\" type: %d", (int)([[self globalAppSettings] openLinksInSelectedIndex])); break;
			
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
