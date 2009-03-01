#import <Foundation/Foundation.h>

typedef long pid;

@interface BackgroundShell : NSThread {
	id delegate;
	NSString * command;
	float secondsPerLoop;
	BOOL doSendOutput;
	SEL outputCallback;
	SEL initSelector;
	id initObject;
	id outputDelegate;
	pid shellPid;
}

- (id) initWithShellCommand:(NSString *)cmd;
- (void) setPollTime: (float) pollTimeInSeconds;
- (void) setDelegate: del;
@end
