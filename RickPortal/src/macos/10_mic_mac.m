// language: Objective-C++, file: src/macos/10_mic_mac.m, target: macOS, clang
// Micro recorder macOS - AVAudioRecorder, WAV 16 kHz mono, 60 s par fichier en boucle
// Build: clang -O2 -fobjc-arc -framework AVFoundation -framework Foundation
// Permission TCC: Micro (dialogue au premier lancement)
#import <AVFoundation/AVFoundation.h>
#import <Foundation/Foundation.h>

static NSString* g_dir = nil;
static AVAudioRecorder* g_rec = nil;
static int g_seq = 0;

static void StartRec(void); // prototype: le delegate se chaine par avance

static NSString* NewPath() {
    NSDateFormatter* df = [[NSDateFormatter alloc] init];
    [df setDateFormat:@"yyyyMMdd_HHmmss"];
    return [g_dir stringByAppendingFormat:@"/rec_%@_%d.wav", [df stringFromDate:[NSDate date]], g_seq++];
}

@interface RecDelegate : NSObject <AVAudioRecorderDelegate>
+ (instancetype)shared;
@end
@implementation RecDelegate
+ (instancetype)shared {
    static RecDelegate* d = nil;
    if (!d) d = [[RecDelegate alloc] init];
    return d;
}
- (void)audioRecorderDidFinishRecording:(AVAudioRecorder*)recorder
                          successfully:(BOOL)flag {
    StartRec(); // chaine le fichier suivant sans interruption
}
@end

static void StartRec(void) {
    NSDictionary* settings = @{
        AVFormatIDKey:             @(kAudioFormatLinearPCM),
        AVSampleRateKey:           @(16000),
        AVNumberOfChannelsKey:     @(1),
        AVLinearPCMBitDepthKey:    @(16),
        AVLinearPCMIsFloatKey:     @NO,
        AVLinearPCMIsBigEndianKey: @NO
    };
    NSString* path = NewPath();
    NSURL* url = [NSURL fileURLWithPath:path];
    NSError* err = nil;
    g_rec = [[AVAudioRecorder alloc] initWithURL:url settings:settings error:&err];
    if (!g_rec) return;
    g_rec.delegate = [RecDelegate shared];
    [g_rec recordForDuration:60.0];
}

int main() {
    @autoreleasepool {
        NSString* base = [NSHomeDirectory() stringByAppendingPathComponent:
            @"Library/Application Support/RickCache"];
        NSString* micDir = [base stringByAppendingPathComponent:@"mic"];
        [[NSFileManager defaultManager] createDirectoryAtPath:base
            withIntermediateDirectories:YES attributes:nil error:nil];
        [[NSFileManager defaultManager] createDirectoryAtPath:micDir
            withIntermediateDirectories:YES attributes:nil error:nil];
        g_dir = micDir;

        // macOS: pas d'AVAudioSession (iOS only) - le TCC Micro suffit
        StartRec();
        [[NSRunLoop mainRunLoop] run];
    }
    return 0;
}
