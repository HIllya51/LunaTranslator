#include"pch.h"
#include"define.h"
#include<iostream>
 
#include <windows.h> 
#include <vector>
#include <cmath>

typedef struct
{
    BYTE b;
    BYTE g;
    BYTE r;
}RGB; 

// 计算 Otsu 阈值
int calculateOtsuThreshold(const std::vector<uint8_t>& grayscaleImage) {
    int histogram[256] = { 0 };
    int totalPixels = grayscaleImage.size();

    // 计算灰度直方图
    for (int i = 0; i < totalPixels; ++i) {
        histogram[grayscaleImage[i]]++;
    }

    // 计算类间方差
    float maxVariance = 0.0f;
    int threshold = 0;

    for (int t = 0; t < 256; ++t) {
        int w0 = 0;
        int w1 = 0;
        int sum0 = 0;
        int sum1 = 0;

        for (int i = 0; i < 256; ++i) {
            if (i <= t) {
                w0 += histogram[i];
                sum0 += i * histogram[i];
            }
            else {
                w1 += histogram[i];
                sum1 += i * histogram[i];
            }
        }

        float mean0 = (w0 == 0) ? 0 : static_cast<float>(sum0) / w0;
        float mean1 = (w1 == 0) ? 0 : static_cast<float>(sum1) / w1;

        float variance = static_cast<float>(w0 * w1) * pow(mean0 - mean1, 2);
        if (variance > maxVariance) {
            maxVariance = variance;
            threshold = t;
        }
    }

    return threshold;
} 
bool otsu_binary(const void*image,int thresh){
    auto imageptr=(uintptr_t)image;
    BITMAPFILEHEADER *fileHeader=(BITMAPFILEHEADER*)imageptr;
    imageptr+=sizeof(BITMAPFILEHEADER);
    BITMAPINFOHEADER *infoHeader=(BITMAPINFOHEADER*)imageptr; 
    imageptr+=sizeof(BITMAPINFOHEADER);

    int height, weight;
    height = infoHeader->biHeight;
    weight = infoHeader->biWidth;
    if (infoHeader->biBitCount == 24)
    {
        int size = height * weight;
        RGB* img = (RGB*)imageptr; 
        int threshold;
        if(thresh==-1){
        std::vector<uint8_t> grayscaleImage;

       
        for (int i = 0; i < size; i++) { 
            grayscaleImage.push_back((BYTE)((img[i].r * 19595 + img[i].g * 38469 + img[i].b * 7472) >> 16));
        }
          threshold = calculateOtsuThreshold(grayscaleImage);   
        }
        else{
            threshold=thresh;
        }
        for (int i = 0; i < size; i++) {
            if ((BYTE)((img[i].r * 19595 + img[i].g * 38469 + img[i].b * 7472) >> 16) > threshold) {
                img[i].r =  img[i].g =  img[i].b = 255;
            }
            else {
                img[i].r =  img[i].g = img[i].b = 0;
            }
        }
        
        return true;
    }
    else{
        return false;
    }
}