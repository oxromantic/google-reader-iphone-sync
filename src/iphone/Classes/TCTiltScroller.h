#import <UIKit/UIKit.h>
#import "ItemView.h"

#define TILT_SCROLL

@interface TCTiltScroller : NSObject {
	float ax, ay, az; // acceleration
	float rx, ry, rz; // 
	float vVelocity, hVelocity;
	float lastTime;
	float startAngle;
	
	// IBOutlet UILabel * label;
	IBOutlet ItemView * scrollView;
	IBOutlet id mainController;
	float last_diff_in_pixels;
	
	int iterations;
	BOOL enabled;
	BOOL paused;
	
	UIInterfaceOrientation uiOrientation;
	UIInterfaceOrientation deviceOrientation;
}

// testing:
- (IBAction) stop: (id) x;
- (IBAction) start: (id) x;
- (IBAction) toggle: (id) sender;

- (void) handleTilt:(float) tilt roll:(float) roll;
@end

