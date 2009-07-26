#import <UIKit/UIKit.h>
#import "TCHelpers.h"

@interface HelpController : NSObject {
	IBOutlet id smallText1;
	IBOutlet id smallText2;
	IBOutlet id smallText3;
	IBOutlet id smallText4;
}

- (IBAction) goIssues:(id)sender;
- (IBAction) goWiki:(id)sender;
- (IBAction) goHome:(id)sender;

- (IBAction) emailSyncLog:(id)sender;
- (IBAction) emailAppLog:(id)sender;

@end
