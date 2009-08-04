#import "TCTiltScroller.h"
#import "TCHelpers.h"
#import <math.h>

#ifdef TILT_SCROLL
#define INTERVAL 0.05
#define CUSHION 0.2
#define SENSITIVITY 0.4
#define DEAD_AREA_DEGREES 5
#define MAX_ANGLE 40

static id instance;
static id iterations;

@implementation TCTiltScroller

+ (id) instance {
	if(!instance) [[TCTiltScroller alloc] init];
	return instance;
}

- (void) awakeFromNib {
	[mainController addInterestedView: self];
	[super awakeFromNib];
}

- (void) acceleratedInX:(float) newx Y:(float) newy Z:(float) newz {
	static float orig_tilt;
	static float x, y, z;
	float tilt;
	
	if((!enabled) ||  paused) return;
	if(iterations < 10) iterations++;
	
	x = x + CUSHION * (newx - x);
	y = y + CUSHION * (newy - y);
	z = z + CUSHION * (newz - z);
	
	tilt = atanf(y/z);
	tilt = (tilt / (2 * 3.14159)) * 360;
	
	if(iterations < 3) return;
	if(iterations == 3) {
		orig_tilt = tilt;
	}
	
	tilt -= orig_tilt;
	if(tilt < -180) tilt += 360;
	if(tilt >  180) tilt -= 360;
	
	// dbg(@"tilt orig = %f, tilt now = %f", orig_tilt, tilt);
	
	// [label setText: [NSString stringWithFormat: @"(%0.1f, %0.1f, %0.1f) => %0.3f", x, y, z, tilt * SENSITIVITY]];
	[self handleTilt: tilt roll: 0.0];
}

- (id) init {
	self = [super init];
	instance = self;
	return self;
}

- (void) didRotateFromInterfaceOrientation: (UIInterfaceOrientation)orientation {
	deviceOrientation = orientation;
	uiOrientation = orientation;
}

- (void) startTiltScroll {
	iterations = 0;
	enabled = YES;
	paused = NO;
}

- (IBAction) stop: (id) sender { [self stopTiltScroll]; }
- (IBAction) start: (id) sender { [self startTiltScroll]; }
- (IBAction) toggle: (id) sender {
	if(enabled) {
		[self stopTiltScroll];
	} else {
		[self startTiltScroll];
	}
	dbg(@"tilt scroll is now %s", enabled ? "ON" : "OFF");
}

- (void) pause { paused = YES; }
- (void) resume { paused = NO; }

- (void) stopTiltScroll {
	enabled = NO;
}

- (void) handleTilt:(float) tilt roll:(float) roll {
	CGRect rect = CGRectMake(0, 0, 1,1);
	float v_pixel_diff = tilt * SENSITIVITY;
	float h_pixel_diff = roll * SENSITIVITY;
	
	// dbg(@"tilt = %0.2f >>> %0.4f, %0.4f", tilt, v_pixel_diff, h_pixel_diff);
	
	[scrollView scrollVertically: v_pixel_diff];
}

- (void)dealloc {
	instance = nil;
	[self stopTiltScroll];
	[super dealloc];
}


@end
#endif