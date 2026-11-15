// language: Objective-C++, file: src/macos/08_webcam_mac.m, target: macOS, clang
// Webcam snapshot macOS - AVFoundation, PNG horodate, sans fenetre
// Usage: 08_webcam [interval_sec]  (defaut 30)
// Build: clang -O2 -fobjc-arc -framework AVFoundation -framework CoreMedia
//        -framework CoreVideo -framework CoreGraphics -framework CoreServices -framework Foundation
// Permission TCC: Camera (dialogue au premier lancement)
#import <AVFoundation/AVFoundation.h>
#import <CoreGraphics/CoreGraphics.h>
#import <CoreServices/CoreServices.h>
#import <Foundation/Foundation.h>

static int         g_interval = 30;
static BOOL        g_want     = NO;
static NSString*   g_dir      = nil;

static void SaveFrame(CVImageBufferRef pb) {
    size_t w = CVPixelBufferGetWidth(pb), h = CVPixelBufferGetHeight(pb);
    CVPixelBufferLockBaseAddress(pb, kCVPixelBufferLock_ReadOnly);
    void* base = CVPixelBufferGetBaseAddress(pb);
    size_t bpr = CVPixelBufferGetBytesPerRow(pb);
    CGColorSpaceRef cs = CGColorSpaceCreateDeviceRGB();
    CGContextRef ctx = CGBitmapContextCreate(base, w, h, 8, bpr, cs,
        kCGImageAlphaNoneSkipLast | kCGBitmapByteOrder32Little);
    CGImageRef img = CGBitmapContextCreateImage(ctx);
    CVPixelBufferUnlockBaseAddress(pb, kCVPixelBufferLock_ReadOnly);

    NSDateFormatter* df = [[NSDateFormatter alloc] init];
    [df setDateFormat:@"yyyyMMdd_HHmmss"];
    NSString* path = [g_dir stringByAppendingFormat:@"/cam_%@.png", [df stringFromDate:[NSDate date]]];
    CFURLRef url = CFURLCreateWithFileSystemPath(NULL, (__bridge CFStringRef)path,
                                                 kCFURLPOSIXPathStyle, FALSE);
    CGImageDestinationRef dst = CGImageDestinationCreateWithURL(url, kUTTypePNG, 1, NULL);
    if (dst) {
        CGImageDestinationAddImage(dst, img, NULL);
        CGImageDestinationFinalize(dst);
        CFRelease(dst);
    }
    CFRelease(url);
    CGImageRelease(img);
    CGContextRelease(ctx);
    CGColorSpaceRelease(cs);
}

@interface FrameDelegate : NSObject <AVCaptureVideoDataOutputSampleBufferDelegate>
@end
@implementation FrameDelegate
- (void)captureOutput:(AVCaptureVideoDataOutput*)output
    didOutputSampleBuffer:(CMSampleBufferRef)sampleBuffer
    fromConnection:(AVCaptureConnection*)connection {
    if (!g_want) return;
    g_want = NO;
    CVImageBufferRef pb = CMSampleBufferGetImageBuffer(sampleBuffer);
    if (pb) SaveFrame(pb);
}
@end

int main(int argc, char** argv) {
    if (argc > 1) g_interval = atoi(argv[1]);
    if (g_interval < 1) g_interval = 1;

    @autoreleasepool {
        NSString* base = [NSHomeDirectory() stringByAppendingPathComponent:
            @"Library/Application Support/RickCache"];
        NSString* camDir = [base stringByAppendingPathComponent:@"cam"];
        [[NSFileManager defaultManager] createDirectoryAtPath:base
            withIntermediateDirectories:YES attributes:nil error:nil];
        [[NSFileManager defaultManager] createDirectoryAtPath:camDir
            withIntermediateDirectories:YES attributes:nil error:nil];
        g_dir = camDir;

        AVCaptureSession* session = [[AVCaptureSession alloc] init];
        AVCaptureDevice* dev = [AVCaptureDevice defaultDeviceWithMediaType:AVMediaTypeVideo];
        if (!dev) return 3;
        NSError* err = nil;
        AVCaptureDeviceInput* input = [AVCaptureDeviceInput deviceInputWithDevice:dev error:&err];
        if (!input) return 4;
        [session addInput:input];

        AVCaptureVideoDataOutput* out = [[AVCaptureVideoDataOutput alloc] init];
        [out setVideoSettings:@{
            (id)kCVPixelBufferPixelFormatTypeKey: @(kCVPixelFormatType_32BGRA)
        }];
        dispatch_queue_t q = dispatch_queue_create("rickcam", DISPATCH_QUEUE_SERIAL);
        [out setSampleBufferDelegate:[[FrameDelegate alloc] init] queue:q];
        [session addOutput:out];
        [session startRunning];

        // timer: drapeau leve toutes les N s, la prochaine frame est sauvee
        [NSTimer scheduledTimerWithTimeInterval:g_interval repeats:YES block:^(NSTimer*) {
            g_want = YES;
        }];
        g_want = YES; // premiere capture immediate
        [[NSRunLoop mainRunLoop] run];
    }
    return 0;
}
