#import "TouchyView.h"

@implementation UIView(TouchyView)

- (void)touchesBegan:(NSSet *)touches withEvent:(UIEvent *)event {
	dbg(@"%@ - touched!", self);
	UITouch * touch = [touches anyObject];
	
	[super touchesBegan:touches withEvent:event];
}

@end
