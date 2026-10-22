#import <UIKit/UIKit.h>

@implementation LegacyObjC
- (void)layout {
    CGRect screen = [UIScreen mainScreen].bounds; // expect: L1
    UIToolbar *bar = [[UIToolbar alloc] init]; // expect: B1
    if ([UIDevice currentDevice].orientation == UIDeviceOrientationPortrait) { } // expect: L2
    if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad) { } // expect: L2
}
@end
