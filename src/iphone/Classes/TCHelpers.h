#import <Foundation/Foundation.h>

#ifdef DEBUG
	#define dbg NSLog
#else
	#define dbg NSLog /*( ... ) {}*/
#endif

#ifdef SIMULATOR
	#define dbg_s NSLog
#else
	#define dbg_s( ... ) {}
#endif

#define _lang(s,desc) NSLocalizedString(s, desc)

@interface TCHelpers : NSObject {
}
+ (BOOL) ensureDirectoryExists:(NSString *)path;
+ (void) alertCalled: (NSString *) title saying: (NSString *) msg;
+ (NSUInteger) lastIndexInPath: (NSIndexPath *) indexPath;
@end
