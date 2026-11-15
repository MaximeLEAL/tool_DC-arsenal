// language: C++ (Arduino / ESP32-S3), file: firmware/JokerPayloadExec.ino
// SGP CARD JOKER - interpreteur Ducky-lite standalone (lab autorise)
// Lit /payload.txt sur LittleFS, l'injecte en clavier USB HID, LED joker + rire a la fin.
// Board: ESP32S3 Dev Module · USB-OTG (TinyUSB) · 8MB flash · partition 8M w/ spiffs · PSRAM off
// Libs: coeur arduino-esp32 3.x (Keyboard incluse en mode USB-OTG)
//
// NOTE: sketch autonome de test - il ne remplace PAS le firmware officiel v1.0.
// Integration dans SGP_Card_Joker.ino : a faire apres inspection du repo officiel.

#include <Arduino.h>
#include <USB.h>
#include <USBHIDKeyboard.h>
#include <LittleFS.h>
#include <Adafruit_NeoPixel.h>
#include <driver/ledc.h>

// clavier HID natif du coeur 3.x (USB-OTG)
USBHIDKeyboard Keyboard;

// ---- pin map officiel SGP Card Joker (config.h v1.0) ----
#define PIN_RGB     10
#define PIN_BUZZER  1
#define PIN_BTN_USR 9
#define NUM_LED     4

Adafruit_NeoPixel leds(NUM_LED, PIN_RGB, NEO_GRB + NEO_KHZ800);

// ---- Ducky-lite : commandes supportees ----
// DELAY <ms> | STRING <texte> | ENTER | GUI <touche?> | CTRL <touche> | ALT <touche> |
// TAB | ESC | DOWN/UP/LEFT/RIGHT | REM ...
// (syntaxe DuckyScript classique - compatibilite exacte avec l'interpreteur
//  officiel de la carte a valider sur le firmware reel)

static void jokerColor(uint32_t c) {
    for (int i = 0; i < NUM_LED; i++) leds.setPixelColor(i, c);
    leds.show();
}

static void buzz(uint32_t freq, uint32_t ms) {
    ledcWriteTone(PIN_BUZZER, freq);
    delay(ms);
    ledcWriteTone(PIN_BUZZER, 0);
}

static void press(const char* k) {
    if      (!strcmp(k, "ENTER")) Keyboard.write(KEY_RETURN);
    else if (!strcmp(k, "TAB"))   Keyboard.write(KEY_TAB);
    else if (!strcmp(k, "ESC"))   Keyboard.write(KEY_ESC);
    else if (!strcmp(k, "DOWN"))  Keyboard.write(KEY_DOWN_ARROW);
    else if (!strcmp(k, "UP"))    Keyboard.write(KEY_UP_ARROW);
    else if (!strcmp(k, "LEFT"))  Keyboard.write(KEY_LEFT_ARROW);
    else if (!strcmp(k, "RIGHT")) Keyboard.write(KEY_RIGHT_ARROW);
    else if (!strcmp(k, "SPACE")) Keyboard.write(' ');
    else Keyboard.write(toupper(k[0]));
}

static void modPress(char mod, const char* k) {
    if (mod == 'G') Keyboard.press(KEY_LEFT_GUI);
    if (mod == 'C') Keyboard.press(KEY_LEFT_CTRL);
    if (mod == 'A') Keyboard.press(KEY_LEFT_ALT);
    if (mod == 'S') Keyboard.press(KEY_LEFT_SHIFT);
    delay(80);
    press(k);
    delay(80);
    Keyboard.releaseAll();
}

static void runPayload(const char* path) {
    File f = LittleFS.open(path, "r");
    if (!f) { jokerColor(0x800000); return; }   // rouge : pas de payload

    String line;
    jokerColor(0x00A000);                       // vert : execution
    while (f.available()) {
        line = f.readStringUntil('\n');
        line.trim();
        if (!line.length() || line.startsWith("REM")) continue;

        if (line.startsWith("DELAY ")) { delay(line.substring(6).toInt()); continue; }
        if (line.startsWith("STRING ")) { Keyboard.print(line.substring(7)); continue; }
        if (line == "ENTER") { press("ENTER"); continue; }
        if (line == "TAB")   { press("TAB");   continue; }
        if (line == "ESC")   { press("ESC");   continue; }
        if (line == "SPACE") { press("SPACE"); continue; }
        if (line.startsWith("GUI "))   { modPress('G', line.substring(4).c_str()); continue; }
        if (line.startsWith("CTRL "))  { modPress('C', line.substring(5).c_str()); continue; }
        if (line.startsWith("ALT "))   { modPress('A', line.substring(4).c_str()); continue; }
        if (line.startsWith("CTRL-SHIFT ")) {
            Keyboard.press(KEY_LEFT_CTRL); Keyboard.press(KEY_LEFT_SHIFT);
            delay(80); press(line.substring(12).c_str()); delay(80); Keyboard.releaseAll();
            continue;
        }
        if (line.startsWith("GUI-") || line.startsWith("CTRL-") || line.startsWith("ALT-")) {
            char m = line[0];
            modPress(m, line.substring(5).c_str());
            continue;
        }
    }
    f.close();
    jokerColor(0x00FF00);                       // vert vif : fini
    buzz(600, 120); buzz(900, 180);             // petit riff joker
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_BTN_USR, INPUT_PULLUP);
    leds.begin();
    jokerColor(0x202000);                       // jaune sombre : boot
    // LEDC pour le buzzer (GPIO1) - API core 3.x
    ledcAttach(PIN_BUZZER, 440, 8);
    buzz(880, 150);

    if (!LittleFS.begin(true)) { jokerColor(0xFF0000); while (1) delay(1000); }

    Keyboard.begin();
    delay(500);                                  // laisse l'OS enumerer le HID
    runPayload("/payload.txt");                  // le payload depose via le panel Storage
}

void loop() {
    // SW4 : relance le payload a la demande (comme le rire officiel, version lab)
    if (digitalRead(PIN_BTN_USR) == LOW) {
        delay(50);
        if (digitalRead(PIN_BTN_USR) == LOW) {
            runPayload("/payload.txt");
            while (digitalRead(PIN_BTN_USR) == LOW) delay(10);
        }
    }
    delay(10);
}
