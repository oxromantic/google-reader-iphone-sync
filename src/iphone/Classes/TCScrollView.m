#import "TCScrollView.h"
#import "TCHelpers.h"


@implementation TCScrollView
- (void) awakeFromNib {
	[mainController addInterestedView: self];
}

- (void) setContentView: (id) view {
	[view retain];
	[contentView release];
	for (id v in [self subviews]) {
		[v removeFromSuperview];
	}
	contentView = view;
	[self insertSubview: contentView atIndex: 0];
	[self _layout];
}

- (void) _layout {
	[contentView layoutIfNeeded];
	[self setContentSize: [contentView bounds].size];
}

- (void) didRotateFromInterfaceOrientation:(UIInterfaceOrientation)previousOrientation {
	[self _layout];
}

@end
