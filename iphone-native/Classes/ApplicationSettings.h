#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface ApplicationSettings : NSObject {
	NSString * docsPath;
	NSMutableDictionary * plistData;
	NSString * plistName;
	
	IBOutlet id emailField;
	IBOutlet id passwordField;
	IBOutlet id itemsPerFeedSlider;
	IBOutlet id itemsPerFeedLabel;
}
-(NSString *) docsPath;
-(NSString *) email;
-(NSString *) password;
-(int) itemsPerFeed;

- (IBAction) itemsPerFeedDidChange: (id) sender;
- (IBAction) stringValueDidChange:(id)sender;

- (IBAction) activatePasswordField:(id)sender;
- (IBAction) deactivateBothFields:(id)sender;
- (IBAction) textFieldDidEndEditing:(UITextField *)sender;

@end