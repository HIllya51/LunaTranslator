#include "OcrLite.h"
#include "OcrUtils.h"
#include <stdarg.h> //windows&linux

OcrLite::OcrLite() {}

OcrLite::~OcrLite() {
    if (isOutputResultTxt) {
        fclose(resultTxt);
    }
}

void OcrLite::setNumThread(int numOfThread) {
    dbNet.setNumThread(numOfThread);
    angleNet.setNumThread(numOfThread);
    crnnNet.setNumThread(numOfThread);
}
 

void OcrLite::enableResultTxt(const char *path, const char *imgName) {
    isOutputResultTxt = true;
    std::string resultTxtPath = getResultTxtFilePath(path, imgName);
    //printf("resultTxtPath(%s)\n", resultTxtPath.c_str());
    resultTxt = fopen(resultTxtPath.c_str(), "w");
}

void OcrLite::setGpuIndex(int gpuIndex) {
    dbNet.setGpuIndex(gpuIndex);
    angleNet.setGpuIndex(-1);
    crnnNet.setGpuIndex(gpuIndex);
}

bool OcrLite::initModels(const std::string &detPath, const std::string &clsPath,
                         const std::string &recPath, const std::string &keysPath) {
    //Logger("=====Init Models=====\n");
    //Logger("--- Init DbNet ---\n");
    dbNet.initModel(detPath);

    ////Logger("--- Init AngleNet ---\n");
    //angleNet.initModel(clsPath);

    //Logger("--- Init CrnnNet ---\n");
    crnnNet.initModel(recPath, keysPath);

    //Logger("Init Models Success!\n");
    return true;
}
 

cv::Mat makePadding(cv::Mat &src, const int padding) {
    if (padding <= 0) return src;
    cv::Scalar paddingScalar = {255, 255, 255};
    cv::Mat paddingSrc;
    cv::copyMakeBorder(src, paddingSrc, padding, padding, padding, padding, cv::BORDER_ISOLATED, paddingScalar);
    return paddingSrc;
}

OcrResult OcrLite::detect(const char *path, const char *imgName,
                          const int padding, const int maxSideLen,
                          float boxScoreThresh, float boxThresh, float unClipRatio, bool doAngle, bool mostAngle) {
    std::string imgFile = getSrcImgFilePath(path, imgName);

    cv::Mat originSrc = imread(imgFile, cv::IMREAD_COLOR);//default : BGR
    int originMaxSide = (std::max)(originSrc.cols, originSrc.rows);
    int resize;
    if (maxSideLen <= 0 || maxSideLen > originMaxSide) {
        resize = originMaxSide;
    } else {
        resize = maxSideLen;
    }
    resize += 2 * padding;
    cv::Rect paddingRect(padding, padding, originSrc.cols, originSrc.rows);
    cv::Mat paddingSrc = makePadding(originSrc, padding);
    ScaleParam scale = getScaleParam(paddingSrc, resize);
    OcrResult result;
    result = detect(path, imgName, paddingSrc, paddingRect, scale,
                    boxScoreThresh, boxThresh, unClipRatio, doAngle, mostAngle);
    return result;
}

OcrResult OcrLite::detect(const cv::Mat &mat, int padding, int maxSideLen, float boxScoreThresh, float boxThresh,
                          float unClipRatio, bool doAngle, bool mostAngle) {
    cv::Mat originSrc = mat;
    int originMaxSide = (std::max)(originSrc.cols, originSrc.rows);
    int resize;
    if (maxSideLen <= 0 || maxSideLen > originMaxSide) {
        resize = originMaxSide;
    } else {
        resize = maxSideLen;
    }
    resize += 2 * padding;
    cv::Rect paddingRect(padding, padding, originSrc.cols, originSrc.rows);
    cv::Mat paddingSrc = makePadding(originSrc, padding);
    ScaleParam scale = getScaleParam(paddingSrc, resize);
    OcrResult result;
    result = detect(NULL, NULL, paddingSrc, paddingRect, scale,
                    boxScoreThresh, boxThresh, unClipRatio, doAngle, mostAngle);
    return result;
}

std::vector<cv::Mat> OcrLite::getPartImages(cv::Mat &src, std::vector<TextBox> &textBoxes,
                                            const char *path, const char *imgName) {
    std::vector<cv::Mat> partImages;
    for (size_t i = 0; i < textBoxes.size(); ++i) {
        cv::Mat partImg = getRotateCropImage(src, textBoxes[i].boxPoint);
        partImages.emplace_back(partImg);
        //OutPut DebugImg
        if (isOutputPartImg) {
            std::string debugImgFile = getDebugImgFilePath(path, imgName, i, "-part-");
            saveImg(partImg, debugImgFile.c_str());
        }
    }
    return partImages;
}

OcrResult OcrLite::detect(const char *path, const char *imgName,
                          cv::Mat &src, cv::Rect &originRect, ScaleParam &scale,
                          float boxScoreThresh, float boxThresh, float unClipRatio, bool doAngle, bool mostAngle) {



    //Logger("=====Start detect=====\n");
    // //Logger("ScaleParam(sw:%d,sh:%d,dw:%d,dh:%d,%f,%f)\n", scale.srcWidth, scale.srcHeight,
    //        scale.dstWidth, scale.dstHeight,
    //        scale.ratioWidth, scale.ratioHeight);

    //Logger("---------- step: dbNet getTextBoxes ----------\n");
    double startTime = getCurrentTime();
    std::vector<TextBox> textBoxes = dbNet.getTextBoxes(src, scale, boxScoreThresh, boxThresh, unClipRatio);
    double endDbNetTime = getCurrentTime();
    double dbNetTime = endDbNetTime - startTime;
    //Logger("dbNetTime(%fms)\n", dbNetTime);

    // for (size_t i = 0; i < textBoxes.size(); ++i) {
    //     //Logger("TextBox[%d](+padding)[score(%f),[x: %d, y: %d], [x: %d, y: %d], [x: %d, y: %d], [x: %d, y: %d]]\n", i,
    //            textBoxes[i].score,
    //            textBoxes[i].boxPoint[0].x, textBoxes[i].boxPoint[0].y,
    //            textBoxes[i].boxPoint[1].x, textBoxes[i].boxPoint[1].y,
    //            textBoxes[i].boxPoint[2].x, textBoxes[i].boxPoint[2].y,
    //            textBoxes[i].boxPoint[3].x, textBoxes[i].boxPoint[3].y);
    // }
     
    //---------- getPartImages ----------
    std::vector<cv::Mat> partImages = getPartImages(src, textBoxes, path, imgName);

    
    //Rotate partImgs
    for (size_t i = 0; i < partImages.size(); ++i) {
        if (doAngle) {
            partImages.at(i) = matRotateClockWise180(partImages[i]);
           // imwrite("1.jpg",partImages[i]);
        }
    }

    //Logger("---------- step: crnnNet getTextLine ----------\n");
    std::vector<TextLine> textLines = crnnNet.getTextLines(partImages, path, imgName);
    //Log TextLines
    // for (size_t i = 0; i < textLines.size(); ++i) {
    //     //Logger("textLine[%d](%s)\n", i, textLines[i].text.c_str());
    //     std::ostringstream txtScores;
    //     for (size_t s = 0; s < textLines[i].charScores.size(); ++s) {
    //         if (s == 0) {
    //             txtScores << textLines[i].charScores[s];
    //         } else {
    //             txtScores << " ," << textLines[i].charScores[s];
    //         }
    //     }
    //     //Logger("textScores[%d]{%s}\n", i, std::string(txtScores.str()).c_str());
    //     //Logger("crnnTime[%d](%fms)\n", i, textLines[i].time);
    // }


    std::string strRes;
     

    std::vector<TextBlock> textBlocks;
    for (size_t i = 0; i < textLines.size(); ++i) {
        std::vector<cv::Point> boxPoint = std::vector<cv::Point>(4);
        int padding = originRect.x;//padding conversion
        boxPoint[0] = cv::Point(textBoxes[i].boxPoint[0].x - padding, textBoxes[i].boxPoint[0].y - padding);
        boxPoint[1] = cv::Point(textBoxes[i].boxPoint[1].x - padding, textBoxes[i].boxPoint[1].y - padding);
        boxPoint[2] = cv::Point(textBoxes[i].boxPoint[2].x - padding, textBoxes[i].boxPoint[2].y - padding);
        boxPoint[3] = cv::Point(textBoxes[i].boxPoint[3].x - padding, textBoxes[i].boxPoint[3].y - padding);
        TextBlock textBlock{boxPoint, textBoxes[i].score, 0, 1,
                            1, textLines[i].text, textLines[i].charScores, textLines[i].time,
                            1};
        textBlocks.emplace_back(textBlock);

        char xx[1000];
        sprintf(xx, "%d,%d,%d,%d,%d,%d,%d,%d\n", textBoxes[i].boxPoint[0].x, textBoxes[i].boxPoint[0].y,
            textBoxes[i].boxPoint[1].x, textBoxes[i].boxPoint[1].y,
            textBoxes[i].boxPoint[2].x, textBoxes[i].boxPoint[2].y,
            textBoxes[i].boxPoint[3].x, textBoxes[i].boxPoint[3].y);
        strRes.append(xx);
        strRes.append(textBlock.text);
        strRes.append("\n");
    }

    double endTime = getCurrentTime();
    double fullTime = endTime - startTime;
    //Logger("=====End detect=====\n");
    //Logger("FullDetectTime(%fms)\n", fullTime);

    //cropped to original size
     /*

    std::string strRes;
    for (auto &textBlock: textBlocks) {
        strRes.append(textBlock.text);
        strRes.append("\n");
    }*/

    return OcrResult{dbNetTime, textBlocks,  fullTime, strRes};
}