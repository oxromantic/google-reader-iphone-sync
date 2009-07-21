#import "TCScrollView.h"
#import "TCHelpers.h"


@implementation TCScrollView

- (void) awakeFromNib {
	[self insertSubview: contentView atIndex: 0];
	[self _layout];
}

- (void) setContentView: (id) view { contentView = view; }

- (void) _layout {
	[contentView layoutIfNeeded];
	[self setContentSize: [contentView bounds].size];
}

@end
