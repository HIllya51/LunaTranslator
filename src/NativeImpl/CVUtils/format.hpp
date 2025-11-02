#include <opencv2/opencv.hpp>
inline std::unique_ptr<cv::Mat> __cvMatFromBMPRGB888(const void *binptr, size_t size)
{
    auto imageptr = (uintptr_t)binptr;
    BITMAPFILEHEADER *fileHeader = (BITMAPFILEHEADER *)imageptr;
    imageptr += sizeof(BITMAPFILEHEADER);
    BITMAPINFOHEADER *infoHeader = (BITMAPINFOHEADER *)imageptr;
    imageptr += sizeof(BITMAPINFOHEADER);
    auto pixelData = (uintptr_t)binptr + fileHeader->bfOffBits;
    int width = infoHeader->biWidth;
    int height = infoHeader->biHeight;
    // 实际上只会是CV_8UC3；32位这样处理不太对，但懒得管了。
    int rowSize = (infoHeader->biBitCount == 24) ? (((width * 3 + 3) / 4) * 4) : (4 * width);
    auto mat = std::make_unique<cv::Mat>(height, width, (infoHeader->biBitCount == 24) ? CV_8UC3 : CV_8UC4, (void *)pixelData, rowSize);
    cv::flip(*mat, *mat, 0);
    return mat;
}
inline std::unique_ptr<cv::Mat> __cvMatFromBGR888(const void *ptr, int width, int height, int bytesPerLine)
{
    // 从内存初始化cvMat不会进行数据拷贝，当ptr生命周期比cvMat短时，会导致cvMat数据失效，因此需要进行拷贝。
    cv::Mat _1(height, width, CV_8UC3, (void *)ptr, bytesPerLine);
    auto _2 = std::make_unique<cv::Mat>();
    _1.copyTo(*_2);
    return _2;
}
inline std::unique_ptr<cv::Mat> __cvMatFromRGB888(const void *ptr, int width, int height, int bytesPerLine)
{
    cv::Mat _1(height, width, CV_8UC3, (void *)ptr, bytesPerLine);
    // auto _2 = std::make_unique<cv::Mat>();
    //  // 方法 1
    //  cv::cvtColor(_1, *_2, cv::COLOR_RGB2BGR);

    // 方法 2.1：使用 split + merge 交换通道
    // std::vector<cv::Mat> channels;
    // cv::split(_1, channels); // 分离 B, G, R 通道
    // cv::Mat cs[] = {channels[2], channels[1], channels[0]};
    // cv::merge(cs, 3, *_2); // 合并为 R, G, B

    // 方法 2.2：直接使用 cv::mixChannels
    auto _2 = std::make_unique<cv::Mat>(_1.size(), _1.type());
    cv::mixChannels(_1, *_2, {0, 2, 1, 1, 2, 0}); // BGR -> RGB
    return _2;
}