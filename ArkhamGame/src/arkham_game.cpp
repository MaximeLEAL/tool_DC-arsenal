// language: C++17, file: arkham_game.cpp, target: Windows x64 (lab)
// LE LEURRE REEL : Batman Arkham Lab - casse-briques GDI jouable
// C'est un vrai jeu : la cible y joue, pendant que l'installateur travaille.
// Cross-compile: x86_64-w64-mingw32-g++ -O2 -std=c++17 arkham_game.cpp -o ArkhamGame.exe -mwindows -lgdi32
#include <windows.h>
#include <cmath>
#include <cstdio>

#define W 640
#define H 480
#define BR 8
#define BC 10

struct Ball { float x, y, vx, vy; };
static Ball ball{320, 380, 3.2f, -4.0f};
static float paddle = 280.0f;
static bool bricks[BR][BC];
static int score = 0, lives = 3;
static bool over = false;

static void ResetBricks() {
    for (int r = 0; r < BR; r++)
        for (int c = 0; c < BC; c++)
            bricks[r][c] = true;
}

LRESULT CALLBACK Proc(HWND w, UINT m, WPARAM wp, LPARAM lp) {
    switch (m) {
    case WM_CREATE: ResetBricks(); SetTimer(w, 1, 16, NULL); return 0;
    case WM_TIMER: {
        if (!over) {
            ball.x += ball.vx; ball.y += ball.vy;
            if (ball.x < 8 || ball.x > W - 8) ball.vx = -ball.vx;
            if (ball.y < 30) ball.vy = -ball.vy;
            // raquette
            POINT rc; GetCursorPos(&rc);
            ScreenToClient(w, &rc);
            paddle = (float)rc.x - 50;
            if (paddle < 0) paddle = 0;
            if (paddle > W - 100) paddle = W - 100;
            if (ball.y > H - 40 && ball.y < H - 28 && ball.x > paddle && ball.x < paddle + 100 && ball.vy > 0) {
                ball.vy = -fabs(ball.vy);
                ball.vx += (ball.x - (paddle + 50)) * 0.06f;
                if (fabs(ball.vx) > 7) ball.vx = ball.vx > 0 ? 7 : -7;
            }
            if (ball.y > H) {
                if (--lives <= 0) over = true;
                ball = {320, 380, 3.2f, -4.0f};
            }
            // briques
            for (int r = 0; r < BR; r++)
                for (int c = 0; c < BC; c++)
                    if (bricks[r][c]) {
                        float bx = 60.0f + c * 54, by = 60.0f + r * 24;
                        if (ball.x > bx && ball.x < bx + 50 && ball.y > by && ball.y < by + 20) {
                            bricks[r][c] = false;
                            score += 10;
                            ball.vy = -ball.vy;
                            r = BR; c = BC; // une brique par frame
                        }
                    }
            int left = 0;
            for (int r = 0; r < BR; r++) for (int c = 0; c < BC; c++) left += bricks[r][c];
            if (!left) { ResetBricks(); ball = {320, 380, 3.2f, -4.0f}; }
        }
        InvalidateRect(w, NULL, FALSE);
        return 0;
    }
    case WM_KEYDOWN:
        if (wp == VK_ESCAPE) PostQuitMessage(0);
        return 0;
    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC dc = BeginPaint(w, &ps);
        HDC mem = CreateCompatibleDC(dc);
        HBITMAP bmp = CreateCompatibleBitmap(dc, W, H);
        SelectObject(mem, bmp);
        // fond gothique
        RECT full{0, 0, W, H};
        HBRUSH night = CreateSolidBrush(RGB(8, 8, 20));
        FillRect(mem, &full, night);
        SetTextColor(mem, RGB(255, 215, 0));
        SetBkMode(mem, TRANSPARENT);
        SelectObject(mem, GetStockObject(DEFAULT_GUI_FONT));
        TextOut(mem, 10, 8, "BATMAN: ARKHAM LAB - DEMO", 25);
        char hud[64];
        snprintf(hud, 64, "SCORE %d   VIES %d", score, lives);
        SetTextColor(mem, RGB(180, 180, 200));
        TextOut(mem, W - 190, 8, hud, (int)strlen(hud));
        // briques
        HBRUSH b1 = CreateSolidBrush(RGB(120, 40, 40));
        HBRUSH b2 = CreateSolidBrush(RGB(40, 70, 120));
        for (int r = 0; r < BR; r++)
            for (int c = 0; c < BC; c++)
                if (bricks[r][c]) {
                    RECT b{(long)(60 + c * 54), (long)(60 + r * 24),
                           (long)(110 + c * 54), (long)(80 + r * 24)};
                    FillRect(mem, &b, r % 2 ? b1 : b2);
                }
        // raquette
        RECT pd{(long)paddle, H - 32, (long)(paddle + 100), H - 22};
        FillRect(mem, &pd, CreateSolidBrush(RGB(220, 220, 230)));
        // balle
        Ellipse(mem, (int)ball.x - 6, (int)ball.y - 6, (int)ball.x + 6, (int)ball.y + 6);
        if (over) {
            SetTextColor(mem, RGB(255, 60, 60));
            TextOut(mem, 240, 220, "GAME OVER - ESC pour quitter", 28);
        }
        BitBlt(dc, 0, 0, W, H, mem, 0, 0, SRCCOPY);
        DeleteObject(bmp); DeleteDC(mem);
        EndPaint(w, &ps);
        return 0;
    }
    case WM_DESTROY: PostQuitMessage(0); return 0;
    }
    return DefWindowProcA(w, m, wp, lp);
}

int WINAPI WinMain(HINSTANCE hi, HINSTANCE, LPSTR, int) {
    WNDCLASSA wc{};
    wc.lpfnWndProc = Proc;
    wc.hInstance = hi;
    wc.lpszClassName = "ArkhamLab";
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    RegisterClassA(&wc);
    HWND w = CreateWindowExA(0, "ArkhamLab",
        "Batman: Arkham Lab - Demo v1.0", WS_OVERLAPPEDWINDOW & ~WS_MAXIMIZEBOX,
        100, 80, W, H + 40, NULL, NULL, hi, NULL);
    ShowWindow(w, SW_SHOW);
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return 0;
}
