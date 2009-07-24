#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface FeedListDelegate : UITableViewController {
	IBOutlet id appSettings;
	IBOutlet id syncController;
	NSArray * feedList;
	NSArray * selectedFeedList;
	IBOutlet id cell;
}

@end
