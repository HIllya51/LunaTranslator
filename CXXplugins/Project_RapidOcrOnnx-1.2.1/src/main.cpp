#ifndef __JNI__
#ifndef __CLIB__
#include <cstdio>
#include "main.h"
#include "version.h"
#include "OcrLite.h"
#include "OcrUtils.h"
#include <string>
#ifdef _WIN32
#include <windows.h>
#include <windows.h>
#include<string> 
using std::string;
#define BUFSIZE 4096
#endif


int main(int argc, char** argv) {
    if (argc <= 1) {
        return -1;
    }
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
#endif
    std::string modelsDir, modelDetPath, modelClsPath, modelRecPath, keysPath;
    std::string imgPath, imgDir, imgName;
    std::string pipename;
    int numThread = 4;
    int padding = 50;
    int maxSideLen = 1024;
    float boxScoreThresh = 0.5f;
    float boxThresh = 0.3f;
    float unClipRatio = 1.6f;
    bool doAngle = true;
    int flagDoAngle = 1;
    bool mostAngle = true;
    int flagMostAngle = 1;
    int flagGpu = -1;

    int opt;
    int optionIndex = 0;
    while ((opt = getopt_long(argc, argv, "d:1:2:3:4:i:t:p:s:b:o:u:a:A:G:v:h:z", long_options, &optionIndex)) != -1) {
        ////printf("option(-%c)=%s\n", opt, optarg);
        switch (opt) {
        case 'd':
            modelsDir = optarg;
            //printf("modelsPath=%s\n", modelsDir.c_str());
            break;
        case '1':
            modelDetPath = modelsDir + "/" + optarg;
            //printf("model det path=%s\n", modelDetPath.c_str());
            break;
        case '2':
            modelClsPath = modelsDir + "/" + optarg;
            //printf("model cls path=%s\n", modelClsPath.c_str());
            break;
        case '3':
            modelRecPath = modelsDir + "/" + optarg;
            //printf("model rec path=%s\n", modelRecPath.c_str());
            break;
        case '4':
            keysPath = modelsDir + "/" + optarg;
            //printf("keys path=%s\n", keysPath.c_str());
            break;
        case 'i':
            imgPath.assign(optarg);
            imgDir.assign(imgPath.substr(0, imgPath.find_last_of('/') + 1));
            imgName.assign(imgPath.substr(imgPath.find_last_of('/') + 1));
            //printf("imgDir=%s, imgName=%s\n", imgDir.c_str(), imgName.c_str());
            break;
        case 't':
            numThread = (int)strtol(optarg, NULL, 10);
            ////printf("numThread=%d\n", numThread);
            break;
        case 'p':
            padding = (int)strtol(optarg, NULL, 10);
            ////printf("padding=%d\n", padding);
            break;
        case 's':
            maxSideLen = (int)strtol(optarg, NULL, 10);
            ////printf("maxSideLen=%d\n", maxSideLen);
            break;
        case 'b':
            boxScoreThresh = strtof(optarg, NULL);
            ////printf("boxScoreThresh=%f\n", boxScoreThresh);
            break;
        case 'o':
            boxThresh = strtof(optarg, NULL);
            ////printf("boxThresh=%f\n", boxThresh);
            break;
        case 'u':
            unClipRatio = strtof(optarg, NULL);
            ////printf("unClipRatio=%f\n", unClipRatio);
            break;
        case 'a':
            flagDoAngle = (int)strtol(optarg, NULL, 10);
            if (flagDoAngle == 0) {
                doAngle = false;
            }
            else {
                doAngle = true;
            }
            ////printf("doAngle=%d\n", doAngle);
            break;
        case 'A':
            flagMostAngle = (int)strtol(optarg, NULL, 10);
            if (flagMostAngle == 0) {
                mostAngle = false;
            }
            else {
                mostAngle = true;
            }
            ////printf("mostAngle=%d\n", mostAngle);
            break;
        case 'v':
            //printf("%s\n", VERSION);
            return 0;
        case 'h':

            return 0;
        case 'G':
            flagGpu = (int)strtol(optarg, NULL, 10);
            break;
        case 'z':
            pipename = optarg;
            break;
        default:
            break;
            //printf("other option %c :%s\n", opt, optarg);
        }
    }

    OcrLite ocrLite;
    ocrLite.setNumThread(numThread);
     
    ocrLite.setGpuIndex(flagGpu);
    // ocrLite.Logger("=====Input Params=====\n");
    // ocrLite.Logger(
    //         "numThread(%d),padding(%d),maxSideLen(%d),boxScoreThresh(%f),boxThresh(%f),unClipRatio(%f),doAngle(%d),mostAngle(%d),GPU(%d)\n",
    //         numThread, padding, maxSideLen, boxScoreThresh, boxThresh, unClipRatio, doAngle, mostAngle,
    //         flagGpu);

    ocrLite.initModels(modelDetPath, modelClsPath, modelRecPath, keysPath);
    wchar_t wpipename[1024]; 
    swprintf_s(wpipename, 1024, L"\\\\.\\Pipe\\ocrwaitsignal_%hs", pipename.c_str()); 
    while (true) {
        HANDLE hPipe = CreateNamedPipe(wpipename, PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT
            , PIPE_UNLIMITED_INSTANCES, 0, 0, NMPWAIT_WAIT_FOREVER, 0);
        if (ConnectNamedPipe(hPipe, NULL) == NULL) {
            continue;
        }
        OcrResult result = ocrLite.detect(imgDir.c_str(), imgName.c_str(), padding, maxSideLen,
            boxScoreThresh, boxThresh, unClipRatio, doAngle, mostAngle);
        BOOL fSuccess = false;
        DWORD len = 0;
        char buffer[BUFSIZE];
        string recvData = "";
        WriteFile(hPipe, result.strRes.c_str(), result.strRes.length(), &len, NULL);
        /*do
        {
            fSuccess = ReadFile(hPipe, buffer, BUFSIZE * sizeof(char), &len, NULL);
            char buffer2[BUFSIZE + 1] = { 0 };
            memcpy(buffer2, buffer, len);
            recvData.append(buffer2);
            if (!fSuccess || len < BUFSIZE)
                break;
        } while (true);*/

        //WinExec("taskkill /IM voice2.exe /F", SW_HIDE);
        //WinExec("./files/voiceroid2/voice2.exe C:/dataH/Yukari2 C:/tmp/LunaTranslator/files/voiceroid2/aitalked.dll yukari_emo_44 1 1.05 C:/tmp/LunaTranslator/ttscache/1.wav  86 111 105 99 101 82 111 105 100 50 32", SW_HIDE);

       // printf("%s\n", result.strRes.c_str());
    }

    return 0;
}

#endif
#endif