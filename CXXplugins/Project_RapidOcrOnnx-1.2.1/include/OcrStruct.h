#ifndef __OCR_STRUCT_H__
#define __OCR_STRUCT_H__

#include "opencv2/core.hpp"
#include <vector>

struct ScaleParam {
    int srcWidth;
    int srcHeight;
    int dstWidth;
    int dstHeight;
    float ratioWidth;
    float ratioHeight;
};

struct TextBox {
    std::vector<cv::Point> boxPoint;
    float score;
};

struct Angle {
    int index;
    float score;
    double time;
};

struct TextLine {
    std::string text;
    std::vector<float> charScores;
    double time;
};

struct TextBlock {
    std::vector<cv::Point> boxPoint;
    float boxScore;
    int angleIndex;
    float angleScore;
    double angleTime;
    std::string text;
    std::vector<float> charScores;
    double crnnTime;
    double blockTime;
};

struct OcrResult {
    double dbNetTime;
    std::vector<TextBlock> textBlocks; 
    double detectTime;
    std::string strRes;
};

#endif //__OCR_STRUCT_H__
