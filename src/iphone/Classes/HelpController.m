#import "HelpController.h"
#import "ApplicationSettings.h"

@implementation HelpController
- (void) awakeFromNib {
	[super awakeFromNib];
	UIFont * font = [UIFont systemFontOfSize: 12.0];

	// ugh...
	[smallText1 setFont: font];
	[smallText2 setFont: font];
	[smallText3 setFont: font];
	[smallText4 setFont: font];
}

- (void) go: (NSString *) url {
	dbg(@"loading URL: %@", url);
	BOOL loaded = [[UIApplication sharedApplication] openURL: [NSURL URLWithString: url]];
	if (!loaded) {
		NSLog(@"failed to load URL: %@", url);
	}
}

- (void) emailLog:(NSString *) logFile {
	NSString * logFilePath = [[ApplicationSettings docsPath] stringByAppendingPathComponent: logFile];
	NSString * emailUrl = [NSString stringWithFormat: @"mailto:tim3d.junk%%2Bgris%%2Blog@gmail.com?subject=GRiS%%20%@&attachment=%@",
		logFile,
		logFilePath];
	[self go: emailUrl];
}

- (IBAction) goIssues: (id)sender { [self go: @"http://code.google.com/p/gris/issues/list"]; }
- (IBAction) goHome:   (id)sender { [self go: @"http://code.google.com/p/gris/"]; }

- (IBAction) emailAppLog: (id)sender { [self emailLog:@"app.log"]; }
- (IBAction) emailSyncLog:(id)sender { [self emailLog:@"sync.log"]; }

@end
