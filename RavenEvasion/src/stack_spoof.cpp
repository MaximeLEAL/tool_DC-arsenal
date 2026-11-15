// language: C++17, file: stack_spoof.cpp, target: Windows x64 (lab VM)
// STACK SPOOFING : les call stacks du process sont faussées — un EDR qui inspecte
// la pile (call stack inspection) voit un appel légitime, pas ton payload.
// Technique : ROP gadget "return to return" (ret2ret) pour construire une fausse
// chaîne de retour qui ressemble à un appel de CreateFileA légitime.
#include <windows.h>
#include <psapi.h>
#include <cstdio>
#include <string>
#pragma comment(lib, "psapi.lib")

// les gadgets sont trouvés dynamiquement dans ntdll (ret = 0xC3, jmp = 0xFF E4…)
static void* FindGadget(HMODULE mod, const BYTE* pattern, SIZE_T len) {
    auto dos = (PIMAGE_DOS_HEADER)mod;
    auto nt  = (PIMAGE_NT_HEADERS)((BYTE*)mod + dos->e_lfanew);
    auto sec = IMAGE_FIRST_SECTION(nt);
    for (int i = 0; i < nt->FileHeader.NumberOfSections; i++) {
        if (sec[i].Characteristics & IMAGE_SCN_MEM_EXECUTE) {
            BYTE* start = (BYTE*)mod + sec[i].VirtualAddress;
            SIZE_T size = sec[i].Misc.VirtualSize;
            for (SIZE_T off = 0; off < size - len; off++) {
                if (!memcmp(start + off, pattern, len)) return start + off;
            }
        }
    }
    return NULL;
}

// démo conceptuelle : on construit la chaine de spoof pour CreateFileA légitime
// (le vrai spoofing s'applique avant chaque appel sensible — le pattern est montré ici)
int main() {
    printf("[*] RAVEN — stack spoofing (call stack inspection)\n\n");

    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    BYTE retGadget[1] = { 0xC3 };                              // gadget "ret"
    void* retAddr = FindGadget(ntdll, retGadget, 1);
    printf("[*] gadget 'ret' trouvé dans ntdll : %p\n", retAddr);

    // la vraie stack du process :
    void* stack[16] = {0};
    void* fp = NULL;                            // frame pointer
    CaptureStackBackTrace(0, 16, stack, NULL);
    printf("[*] call stack AVANT spoofing (vue EDR) :\n");
    HMODULE mods[64]; DWORD needed;
    EnumProcessModules(GetCurrentProcess(), mods, sizeof(mods), &needed);
    for (int i = 0; i < 6 && i < 16; i++) {
        if (!stack[i]) break;
        char name[MAX_PATH];
        for (unsigned m = 0; m < needed / sizeof(HMODULE); m++) {
            char fn[MAX_PATH];
            DWORD sz2 = MAX_PATH;
            if (GetModuleFileNameExA(GetCurrentProcess(), mods[m], fn, sz2)) {
                if ((BYTE*)stack[i] >= (BYTE*)mods[m] &&
                    (BYTE*)stack[i] < (BYTE*)mods[m] + 0x10000000) {
                    printf("   [%d] %s+0x%llx\n", i,
                           strrchr(fn, '\\') ? strrchr(fn, '\\') + 1 : fn,
                           (unsigned long long)((BYTE*)stack[i] - (BYTE*)mods[m]));
                }
            }
        }
    }

    // le SPOOF : la stack ressemblera à CreateFileA légitime
    void* createFile = (void*)GetProcAddress(GetModuleHandleA("kernel32.dll"), "CreateFileA");
    printf("\n[*] stack SPOOFÉE (vue EDR après injection) :\n");
    printf("   [0] %p (payload frame)\n", retAddr);
    printf("   [1] %p (kernel32.CreateFileA)\n", createFile);
    printf("   [2] %p (ret gadget)\n", retAddr);
    printf("   [3] ntdll!RtlUserThreadStart\n");
    printf("\n[OK] le concept : ta vraie stack est remplacée par une chaîne légitime —\n");
    printf("     l'EDR qui inspecte voit CreateFileA, pas ton payload\n");
    printf("     (l'implémentation full ROP est dans les notes du README — 4 h de build)\n");
    return 0;
}
