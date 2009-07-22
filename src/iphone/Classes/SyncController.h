#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import "BackgroundShell.h"

@interface SyncController : UIViewController {
	IBOutlet id syncStatusView;
	IBOutlet id notSyncingView;
	IBOutlet id cancelButton;
	IBOutlet id okButton;
	IBOutlet id syncOutput;
	IBOutlet id spinner;
	IBOutlet id feedList;
	IBOutlet id appSettings;
	NSMutableArray * syncOutputBuffer;
	
	BackgroundShell * syncThread;
	BOOL syncRunning;
	BOOL developerMode;
	int sync_pid;
	IBOutlet id root;
	
	IBOutlet id itemsController;
	IBOutlet id db;
	
	IBOutlet id status_currentTask;
	IBOutlet id status_taskProgress;
	IBOutlet id status_mainProgress;
	
	int totalTasks;
	int totalStepsInCurrentTask;
	NSString * last_output_line;
}
- (IBAction) sync: (id) sender;
- (IBAction) syncFeedListOnly: (id) sender;
- (IBAction) cancelSync: (id) sender;
- (IBAction) hideSyncView: (id)sender;
- (IBAction) syncStatusOnly: (id) sender;
@end
