#include <cstdio>
#include "main.h"
#include "version.h"
#include "OcrLite.h"
#include "OcrUtils.h"

#ifdef _WIN32
#include <windows.h>
#endif

void printHelp(FILE *out, char *argv0) {
    fprintf(out, " ------- Usage -------\n");
    fprintf(out, "%s %s", argv0, usageMsg);
    fprintf(out, " ------- Required Parameters -------\n");
    fprintf(out, "%s", requiredMsg);
    fprintf(out, " ------- Optional Parameters -------\n");
    fprintf(out, "%s", optionalMsg);
    fprintf(out, " ------- Other Parameters -------\n");
    fprintf(out, "%s", otherMsg);
    fprintf(out, " ------- Examples -------\n");
    fprintf(out, example1Msg, argv0);
    fprintf(out, example2Msg, argv0);
}

int main(int argc, char **argv) {
    if (argc <= 1) {
        printHelp(stderr, argv[0]);
        return -1;
    }
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
#endif
    std::string modelsDir, modelDetPath, modelClsPath, modelRecPath, keysPath;
    std::string imgPath, imgDir, imgName;
    int numThread = 4;
    int loopCount = 1;
    int padding = 50;
    int maxSideLen = 1024;
    float boxScoreThresh = 0.5f;
    float boxThresh = 0.3f;
    float unClipRatio = 1.5f;
    bool doAngle = true;
    int flagDoAngle = 1;
    bool mostAngle = true;
    int flagMostAngle = 1;
    int flagGpu = -1;

    int opt;
    int optionIndex = 0;
    while ((opt = getopt_long(argc, argv, "d:1:2:3:4:i:t:p:s:b:o:u:a:A:G:v:h:l", long_options, &optionIndex)) != -1) {
        //printf("option(-%c)=%s\n", opt, optarg);
        switch (opt) {
            case 'd':
                modelsDir = optarg;
                printf("modelsPath=%s\n", modelsDir.c_str());
                break;
            case '1':
                modelDetPath = modelsDir + "/" + optarg;
                printf("model det path=%s\n", modelDetPath.c_str());
                break;
            case '2':
                modelClsPath = modelsDir + "/" + optarg;
                printf("model cls path=%s\n", modelClsPath.c_str());
                break;
            case '3':
                modelRecPath = modelsDir + "/" + optarg;
                printf("model rec path=%s\n", modelRecPath.c_str());
                break;
            case '4':
                keysPath = modelsDir + "/" + optarg;
                printf("keys path=%s\n", keysPath.c_str());
                break;
            case 'i':
                imgPath.assign(optarg);
                imgDir.assign(imgPath.substr(0, imgPath.find_last_of('/') + 1));
                imgName.assign(imgPath.substr(imgPath.find_last_of('/') + 1));
                printf("imgDir=%s, imgName=%s\n", imgDir.c_str(), imgName.c_str());
                break;
            case 't':
                numThread = (int) strtol(optarg, NULL, 10);
                //printf("numThread=%d\n", numThread);
                break;
            case 'p':
                padding = (int) strtol(optarg, NULL, 10);
                //printf("padding=%d\n", padding);
                break;
            case 's':
                maxSideLen = (int) strtol(optarg, NULL, 10);
                //printf("maxSideLen=%d\n", maxSideLen);
                break;
            case 'b':
                boxScoreThresh = strtof(optarg, NULL);
                //printf("boxScoreThresh=%f\n", boxScoreThresh);
                break;
            case 'o':
                boxThresh = strtof(optarg, NULL);
                //printf("boxThresh=%f\n", boxThresh);
                break;
            case 'u':
                unClipRatio = strtof(optarg, NULL);
                //printf("unClipRatio=%f\n", unClipRatio);
                break;
            case 'a':
                flagDoAngle = (int) strtol(optarg, NULL, 10);
                if (flagDoAngle == 0) {
                    doAngle = false;
                } else {
                    doAngle = true;
                }
                //printf("doAngle=%d\n", doAngle);
                break;
            case 'A':
                flagMostAngle = (int) strtol(optarg, NULL, 10);
                if (flagMostAngle == 0) {
                    mostAngle = false;
                } else {
                    mostAngle = true;
                }
                //printf("mostAngle=%d\n", mostAngle);
                break;
            case 'v':
                printf("%s\n", VERSION);
                return 0;
            case 'h':
                printHelp(stdout, argv[0]);
                return 0;
            case 'G':
                flagGpu = (int) strtol(optarg, NULL, 10);
                break;
            case 'l':
                loopCount = (int) strtol(optarg, NULL, 10);
                //printf("loopCount=%d\n", loopCount);
                break;
            default:
                printf("other option %c :%s\n", opt, optarg);
        }
    }
    bool hasTargetImgFile = isFileExists(imgPath);
    if (!hasTargetImgFile) {
        fprintf(stderr, "Target image not found: %s\n", imgPath.c_str());
        return -1;
    }
    bool hasModelDetFile = isFileExists(modelDetPath);
    if (!hasModelDetFile) {
        fprintf(stderr, "Model det file not found: %s\n", modelDetPath.c_str());
        return -1;
    }
    bool hasModelClsFile = isFileExists(modelClsPath);
    if (!hasModelClsFile) {
        fprintf(stderr, "Model cls file not found: %s\n", modelClsPath.c_str());
        return -1;
    }
    bool hasModelRecFile = isFileExists(modelRecPath);
    if (!hasModelRecFile) {
        fprintf(stderr, "Model rec file not found: %s\n", modelRecPath.c_str());
        return -1;
    }
    bool hasKeysFile = isFileExists(keysPath);
    if (!hasKeysFile) {
        fprintf(stderr, "keys file not found: %s\n", keysPath.c_str());
        return -1;
    }
    OcrLite ocrLite;
    ocrLite.setNumThread(numThread);
   

    //ocrLite.enableResultTxt(imgDir.c_str(), imgName.c_str());
    ocrLite.setGpuIndex(flagGpu);
    printf("=====Input Params=====\n");
    printf("numThread(%d),padding(%d),maxSideLen(%d),boxScoreThresh(%f),boxThresh(%f),unClipRatio(%f),doAngle(%d),mostAngle(%d),GPU(%d)\n",
            numThread, padding, maxSideLen, boxScoreThresh, boxThresh, unClipRatio, doAngle, mostAngle,
            flagGpu);
    bool initModelsRet = ocrLite.initModels(modelDetPath, modelClsPath, modelRecPath, keysPath);
    if (!initModelsRet) return -1;
    printf("=====Warmup 2 cycles=====\n");
    for (int i = 0; i < 2; ++i) {
        OcrResult result = ocrLite.detect(imgDir.c_str(), imgName.c_str(), padding, maxSideLen,
                                          boxScoreThresh, boxThresh, unClipRatio, doAngle, mostAngle);
        printf("Warmup time(%f)\n", result.detectTime);
    }
    printf("=====Start Test Loop=====\n");
    double allDbTime = 0.0f;
    double allClsTime = 0.0f;
    double allRecTime = 0.0f;
    double allFullTime = 0.0f;
    for (int i = 0; i < loopCount; ++i) {
        printf("=====Cycle:%d Take Time(ms)=====\n", i + 1);
        OcrResult ocrResult = ocrLite.detect(imgDir.c_str(), imgName.c_str(),
                                             padding, maxSideLen,
                                             boxScoreThresh, boxThresh,
                                             unClipRatio, doAngle, mostAngle);
        double dbTime = ocrResult.dbNetTime;
        double clsTime = 0.0f;
        double recTime = 0.0f;
        for (const auto &item: ocrResult.textBlocks) {
            clsTime += item.angleTime;
            recTime += item.crnnTime;
        }
        double fullTime = ocrResult.detectTime;
        printf("det=%f cls=%f rec=%f full=%f\n", dbTime, clsTime, recTime, fullTime);
        allDbTime += dbTime;
        allClsTime += clsTime;
        allRecTime += recTime;
        allFullTime += fullTime;
    }
    printf("=====Result:Average Time(ms)=====\n");
    printf("det=%f cls=%f rec=%f full=%f\n", allDbTime / loopCount, allClsTime / loopCount,
           allRecTime / loopCount, allFullTime / loopCount);
    return 0;
}
