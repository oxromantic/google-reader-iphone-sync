#import "SyncController.h"
#import "TCHelpers.h"
#import <stdio.h>

// and for proxy stuff:
#import <CoreFoundation/CoreFoundation.h>
#import <CFNetwork/CFProxySupport.h>


#ifdef SIMULATOR
	// the following function is not defined for the simulator. dammit.
	NSDictionary * CFNetworkCopySystemProxySettings(void){ return NULL; };
	NSArray * fakeProxySettings ( void * a, void * b) {
		dbg(@"returning a fake proxy setting");
		NSDictionary * dict = [NSDictionary dictionaryWithObject: kCFProxyTypeNone forKey: kCFProxyTypeKey];
		return [[NSArray arrayWithObject: dict] retain];
	}
	#define CFNetworkCopyProxiesForURL fakeProxySettings
	#warning "using hacky, faked proxy settings for the iphone simulator"
#else
	#define DEBUG
#endif

typedef enum { Default, FeedList, Status, Singleton } SyncType;

NSDictionary * STATUS_LINES;

@implementation SyncController

NSDictionary * status_lines() {
	if(!STATUS_LINES) {
		STATUS_LINES = [[NSDictionary dictionaryWithObjectsAndKeys:
			@"Authorizing", _lang(@"Authorizing",""),
			@"Pushing status", _lang(@"Pushing status",""),
			@"Cleaning up old resources", _lang(@"Cleaning up old resources",""),
			@"Downloading tag", _lang(@"Downloading tag",""),
			@"Sync complete.", _lang(@"Sync Complete.",""),
			nil] retain];
	}
	return STATUS_LINES;
}

- (NSString *) translateStartOfString:(NSString *) status_line {
	NSBundle * bundle = [NSBundle bundleForClass:[self class]];
	NSString * translatable;
	NSString * translated;
	NSDictionary * _status_lines = status_lines();
	for (id key in _status_lines) { 
		translatable = [_status_lines objectForKey:key];
		if([status_line hasPrefix: translatable]) {
			translated = [bundle localizedStringForKey:translatable value:translatable table:nil];
			status_line = [status_line stringByReplacingOccurrencesOfString: translatable withString: translated];
			break;
		}
	} 
	return status_line;
}

NSString * escape_single_quotes(NSString * str) {
	return [str stringByReplacingOccurrencesOfString:@"'" withString:@"'\"'\"'"];
}

- (NSString *) syncCommandString:(SyncType) syncType {
	id settings = [[[UIApplication sharedApplication] delegate] settings];
	NSMutableString * extra_opts = [NSMutableString string];
	switch(syncType) {
		case FeedList:
			[extra_opts appendString: @" --tag-list-only"];
			break;
		case Status:
			[extra_opts appendString: @" --no-download"];
			break;
		case Singleton:
			[extra_opts appendString: @" --report-pid --loglevel=error"];
			break;
		
	}
	
	if( [[self globalAppSettings] sortNewestItemsFirst] ) {
		[extra_opts appendString: @" --newest-first"];
	}
	
	NSString * shellString = [NSString stringWithFormat:@"python '%@' --show-status --aggressive --config='%@' --output-path='%@' --logdir='%@' %@ 2>&1",
		escape_single_quotes([[settings docsPath] stringByAppendingPathComponent:@"sync/main.py"]),
		escape_single_quotes([[settings docsPath] stringByAppendingPathComponent:@"config.plist"]),
		escape_single_quotes([settings docsPath]),
		escape_single_quotes([settings docsPath]),
		extra_opts];
	
	NSString * proxy = [self proxySettings];
	if(proxy) {
		dbg(@"using proxy string: %@", proxy);
		shellString = [NSString stringWithFormat:@"export http_proxy='%@';export https_proxy='%@';%@", escape_single_quotes(proxy), escape_single_quotes(proxy), shellString];
	}
	dbg_s(@"shell command: %@", shellString);
	return shellString;
}

- (void) syncWithType:(SyncType) syncType {
	if(syncThread && ![syncThread isFinished]) {
		dbg(@"thread is still running!");
		return;
	}

	NSString * shellString = [self syncCommandString:syncType];
	syncThread = [[BackgroundShell alloc] initWithShellCommand: shellString];
	[syncThread setDelegate: self];

	// set up the views
	[spinner setAnimating:YES];
	[spinner setHidden:NO];
	[cancelButton setHidden:YES];
	[okButton setHidden:YES];

	[syncStatusView setHidden:NO];
	[[root view] addSubview: syncStatusView];
	[syncStatusView setAlpha: 1.0];
	[syncStatusView fitToSuperview];
	[[root view] layoutSubviews];
	[self setStatusTextWithoutTranslation: _lang(@"Loading...","")];
	[status_mainProgress setProgress: 0.0];
	[status_taskProgress setProgress: 0.0];
	[status_taskProgress setHidden:NO];
	[status_mainProgress setHidden:NO];
	[self initSyncOutput];
	[self disableSleep];
	
	// animate
	[syncStatusView animateFadeIn];
	
	// reset output
	[last_output_line release];
	last_output_line = nil;
	
	// ..and go!
	[syncThread start];
}

- (IBAction) syncFeedListOnly: (id) sender {
	[self syncWithType:FeedList];
}

- (IBAction) sync: (id) sender {
	[self syncWithType: Default];
}

- (IBAction) syncStatusOnly: (id) sender {
	[self syncWithType: Status];
}

- (BOOL) backgroundShellShouldBegin: (id) bgshell {
	BOOL ret = [self forceInternetConnection];
	if(!ret) {
		last_output_line = _lang(@"No internet connection found","");
	}
	return ret;
}

- (BOOL) forceInternetConnection {
	// grab google's home page; forcing an EDGE/3G connection to be made
	// (python's urlopen seems not to trigger this, so we do it in obj-c land)
	NSURLRequest * request = [NSURLRequest requestWithURL:[NSURL URLWithString: @"http://www.google.com/"] cachePolicy:NSURLRequestReloadIgnoringLocalCacheData timeoutInterval: 20];
	NSURLResponse * response;
	NSData * data = [NSURLConnection sendSynchronousRequest: request returningResponse: &response error: nil];
	BOOL success = (data != nil);
	if(!success) {
		dbg(@"PING connection failed");
	}
	return success;
}

- (void) ensureSingletonWorkerAction:(id)obj {
	// setup GC pool
	NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
	
	NSString * cmd = [self syncCommandString:Singleton];
	dbg_s(@"Running command: %@", cmd);
	FILE * output = popen([cmd cStringUsingEncoding: NSUTF8StringEncoding], "r");
	char cline[500];
	NSString * line;
	int pid = 0;
	while(fgets(cline, sizeof(cline) / sizeof(char), output) != NULL) {
		line = [NSString stringWithCString: cline encoding: NSUTF8StringEncoding];
		line = [line stringByTrimmingCharactersInSet: [NSCharacterSet whitespaceAndNewlineCharacterSet]];
		if([line length] > 0) {
			if([line isEqualToString: @"None"]) {
				pid = 0;
				break;
			} else {
				dbg(@"pid got line: [%@]", line);
			}
			pid = [line intValue];
		}
	}
	pclose(output);
	[self performSelector: @selector(dealWithRunningSync:)
		onThread:[NSThread mainThread]
		withObject:[NSNumber numberWithInt: pid]
		waitUntilDone: YES];
	[pool release];
}

- (void) dealWithRunningSync:(NSNumber *) pid_ {
	int pid = [pid_ intValue];
	if(pid > 0) {
		dbg(@"pid = %d", pid);
		sync_pid = pid;
		[[[[UIAlertView alloc]
			initWithTitle:_lang(@"GRiS Sync","") message: _lang(@"There is already a sync running. It is either stuck, or a scheduled sync.\nStop it?","")
			delegate:self cancelButtonTitle:_lang(@"Cancel (quit)","") otherButtonTitles:_lang(@"Stop sync",""), nil]
				autorelease] show];
	}
}

- (void) ensureSingleton {
	[[[[NSThread alloc] initWithTarget:self selector: @selector(ensureSingletonWorkerAction:) object:nil] autorelease] start];
}

- (void) alertView:(id)view clickedButtonAtIndex: (int) index {
	if(index == 1) { // kill it
		kill(sync_pid, SIGKILL);
	} else {
		dbg(@"user opted to exit because there is a background sync running");
		[[UIApplication sharedApplication] terminate];
	}
}

- (void) disableSleep {
	[[UIApplication sharedApplication] setIdleTimerDisabled: YES];
}

- (void) enableSleep {
	[[UIApplication sharedApplication] setIdleTimerDisabled: NO];
}

- (IBAction) cancelSync: (id) sender {
	[self enableSleep];
	if(!syncThread || [syncThread isFinished]) {
		dbg(@"can't cancel sync - it's already finished!");
		return;
	}
	NSLog(@"cancelling thread...");
	last_output_line = _lang(@"Cancelled.","");
	[syncThread cancel];
	[cancelButton setHidden:YES];
}

- (void) syncViewIsGone{
	[syncStatusView setHidden:YES];
	[syncStatusView removeFromSuperview];
	[self clearSyncBuffer];
}

- (NSString *) proxySettings {
	NSString * settings = nil;
	dbg_s(@"grabbing all proxy settings");
	CFDictionaryRef proxySettings = CFNetworkCopySystemProxySettings();
	NSURL * url = [NSURL URLWithString: @"http://google.com"];
	NSArray * proxyConfigs = CFNetworkCopyProxiesForURL(url, proxySettings);
	
	if([proxyConfigs count] > 0) {
		dbg_s(@"proxies: %@", proxyConfigs);
		NSDictionary * bestProxy = [proxyConfigs objectAtIndex: 0];
		NSString * proxyType = [bestProxy objectForKey:kCFProxyTypeKey];
		if( proxyType && proxyType != kCFProxyTypeNone) {
			dbg_s(@"best proxy found: %@ @ %d", bestProxy, bestProxy);
			NSString * host = [bestProxy valueForKey:kCFProxyHostNameKey];
			NSString * port = [bestProxy valueForKey:kCFProxyPortNumberKey];
			NSString * user = [bestProxy valueForKey:kCFProxyUsernameKey];
			NSString * pass = [bestProxy valueForKey:kCFProxyPasswordKey];
		
			settings = [NSString stringWithFormat:@"%@%s%@%s%@%s%@",
				user ? [user stringByAddingPercentEscapesUsingEncoding:NSASCIIStringEncoding] : @"",
				pass ? ":":"",
				pass ? [pass stringByAddingPercentEscapesUsingEncoding:NSASCIIStringEncoding] : @"",
				user ? "@":"",
				host,
				port ? ":":"",
				port ? port : @""];
		}
	}
	
	[proxyConfigs release];
	return settings;
}

- (IBAction) hideSyncView: (id)sender {
	[syncStatusView animateFadeOutThenTell:self withSelector:@selector(syncViewIsGone)];
	[db reload];
	[[[UIApplication sharedApplication] delegate] refreshItemLists];
}

// sync finished but you still want to see the report
- (void) showSyncFinished {
	[status_taskProgress setHidden:YES];
	[status_mainProgress setHidden:YES];

	[spinner setHidden:YES];
	[okButton setHidden:NO];
	[cancelButton setHidden:YES];
	[appSettings reloadFeedList];
}

#pragma mark delegate callbacks
- (void) backgroundShell:(id)shell didFinishWithSuccess:(BOOL) success {
	[self setStatusText:last_output_line];
	[syncThread release];
	syncThread = nil;
	[self showSyncFinished];
	[self enableSleep];
	if([last_output_line hasPrefix:@"Sync complete."] && (!developerMode)) {
		[self hideSyncView:self];
	}
}

- (void) setStatusText: (NSString *) status_line {
	[status_currentTask setText: [self translateStartOfString: status_line]];
}

- (void) setStatusTextWithoutTranslation: (NSString *) status_line {
	[status_currentTask setText: status_line];
}

- (void) backgroundShell:(id)shell didProduceOutput:(NSString *) line {
	dbg_s(@"sync output: %@", line);
	int numStatusComponents;

	if([line hasPrefix:@"STAT:"]){
		NSArray * statusComponents = [line componentsSeparatedByString:@":"];
		numStatusComponents = [statusComponents count];
		if(numStatusComponents > 1) {
			@try{
				NSString * type = [statusComponents objectAtIndex:1];
				if([type isEqualToString:@"TASK_TOTAL"]){
					// total number of tasks
					totalTasks = [[statusComponents objectAtIndex:2] integerValue];
				} else if([type isEqualToString:@"TASK_PROGRESS"]){
					// new sub-task, with optional description
					if(numStatusComponents > 3) {
						[self setStatusText: [statusComponents objectAtIndex:3]];
					}
					[status_mainProgress setProgress: ([[statusComponents objectAtIndex:2] floatValue] / (float)totalTasks )];
					[status_taskProgress setProgress: 0.0];
				} else if([type isEqualToString:@"SUBTASK_TOTAL"]){
					// total number of steps for current subtask
					totalStepsInCurrentTask = [[statusComponents objectAtIndex:2] integerValue];
				} else if([type isEqualToString:@"SUBTASK_PROGRESS"]){
					// progress for current subtask
					[status_taskProgress setProgress: ( [[statusComponents objectAtIndex:2] floatValue] / (float)totalStepsInCurrentTask ) ];
				} else {
					dbg(@"unknown status type: %@", type);
				}
			} @catch(NSException *e) {
				dbg(@"error occurred:\n%@", e);
			}
		}
	} else {
		[self addSyncOutput: line];
		[self setLastOutputLine: line];
	}
}

#define num_sync_lines 100

- (void) setLastOutputLine: (NSString *) line {
		[last_output_line release];
		last_output_line = [line retain];
}

- (void) addSyncOutput:(NSString *) output {
	if(!developerMode) return;
	if([syncOutputBuffer count] >= num_sync_lines) {
		[syncOutputBuffer removeObjectAtIndex:0];
	}
	[syncOutputBuffer addObject: output];
	[syncOutput setText: [self syncOutputString]];
	CGSize content = [syncOutput contentSize];
	CGRect bottomLine = CGRectMake(0,content.height,1,1);
	[syncOutput scrollRectToVisible:bottomLine animated:NO];
}

- (NSString *) syncOutputString {
	return [syncOutputBuffer componentsJoinedByString: @""];
}

- (void) initSyncOutput {
	developerMode = [appSettings developerMode];
	[syncOutputBuffer release];
	syncOutputBuffer = [[NSMutableArray alloc] init];
	[syncOutput setText: @""];
	[syncOutput setHidden: ![appSettings developerMode]];
	[syncOutput setFont: [UIFont systemFontOfSize:11.0]];
}

- (void) clearSyncBuffer {
	[syncOutputBuffer release];
	syncOutputBuffer = nil;
}

@end
