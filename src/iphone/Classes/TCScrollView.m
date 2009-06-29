#import "TCScrollView.h"
#import "TCHelpers.h"


@implementation TCScrollView

- (void) awakeFromNib {
	[self insertSubview: contentView atIndex: 0];
	[self setContentSize: [contentView bounds].size];
	[contentView layoutIfNeeded];
}

- (void) setContentView: (id) view {
	contentView = view;
}

@end
