// language: C++17, file: lex_test_dll.cpp, target: Windows x64
// DLL de test : preuve visuelle d'injection (MessageBox a l'attach)
// cross-compile: x86_64-w64-mingw32-g++ -shared -o lex_test_dll.dll lex_test_dll.cpp -static
#include <windows.h>

BOOL WINAPI DllMain(HINSTANCE, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH)
        MessageBoxA(NULL, "INJECTE - LexCorp was here", "lex_test_dll", MB_OK);
    return TRUE;
}
