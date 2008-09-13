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

@interface TCHelpers : NSObject {
}
+ (BOOL) ensureDirectoryExists:(NSString *)path;
+ (void) alertCalled: (NSString *) title saying: (NSString *) msg;
+ (NSUInteger) lastIndexInPath: (NSIndexPath *) indexPath;
@end
