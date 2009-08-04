#import <UIKit/UIKit.h>
#import "ApplicationSettings.h"
#import "TCHelpers.h"

int main(int argc, char *argv[]) {
	NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];

	#ifndef SIMULATOR
		// redirect stderr to a logfile if we're not on the simulator
		NSString *logPath = [[ApplicationSettings docsPath] stringByAppendingPathComponent: @"app.log"];
		dbg(@"opening logfile at: %@", logPath);
		freopen([logPath fileSystemRepresentation], "w", stderr);
		dbg(@"Logging started");
		[logPath release];
	#endif

	int retVal = UIApplicationMain(argc, argv, @"GRiSApplication", nil);
	[pool release];
	return retVal;
}

