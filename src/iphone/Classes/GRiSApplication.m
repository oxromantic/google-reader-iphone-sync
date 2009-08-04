#import "GRiSApplication.h"
#import "TCTiltScroller.h"

@implementation GRiSApplication

#ifdef TILT_SCROLL
- (void)acceleratedInX:(float)x Y:(float)y Z:(float)z {
	[[TCTiltScroller instance] acceleratedInX: x Y:y Z:z];
}
#endif

@end
