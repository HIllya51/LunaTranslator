#include "ortwrapper.hpp"
#include <opencv2/opencv.hpp>

class CommonOnnxModel : public OnnxSession
{
    const std::array<float, 3> meanValues;
    const std::array<float, 3> normValues;

    std::vector<float> substractMeanNormalize(const cv::Mat &src, const float *meanVals, const float *normVals)
    {
        auto inputTensorSize = src.cols * src.rows * src.channels();
        std::vector<float> inputTensorValues(inputTensorSize);
        size_t numChannels = src.channels();
        size_t imageSize = src.cols * src.rows;

        for (size_t pid = 0; pid < imageSize; pid++)
        {
            for (size_t ch = 0; ch < numChannels; ++ch)
            {
                float data = (float)(src.data[pid * numChannels + ch] * normVals[ch] - meanVals[ch] * normVals[ch]);
                inputTensorValues[ch * imageSize + pid] = data;
            }
        }
        return inputTensorValues;
    }

public:
    std::pair<std::vector<float>, std::vector<int64_t>> RunSession(const cv::Mat &src)
    {
        auto inputTensorValues = substractMeanNormalize(src, meanValues.data(), normValues.data());
        std::array<int64_t, 4> inputShape{1, src.channels(), src.rows, src.cols};
        return OnnxSession::RunSession(inputShape, inputTensorValues);
    }
    CommonOnnxModel(const std::wstring &path, const std::array<float, 3> &_meanValues, const std::array<float, 3> &_normValues, int numOfThread = 4) : meanValues(_meanValues), normValues(_normValues), OnnxSession(path, numOfThread)
    {
    }
};

typedef std::array<cv::Point2f, 4> TextBox;
typedef std::string TextLine;
typedef std::pair<TextBox, TextLine> TextBlock;
enum class Directional
{
    H,
    V,
    Auto
};

struct ScaleParam
{
    int srcWidth;
    int srcHeight;
    int dstWidth;
    int dstHeight;
    float ratioWidth;
    float ratioHeight;
};

class CrnnNet : public CommonOnnxModel
{
public:
    CrnnNet(const std::wstring &pathStr, const std::wstring &keysPath, int numOfThread);
    std::vector<TextLine> getTextLines(const std::vector<cv::Mat> &partImg);

private:
    const int dstHeight = 48;

    std::vector<std::string> keys;

    TextLine scoreToTextLine(const std::vector<float> &outputData, size_t h, size_t w);

    TextLine getTextLine(const cv::Mat &src);
};

class DbNet : public CommonOnnxModel
{
public:
    DbNet(const std::wstring &pathStr, int numOfThread) : CommonOnnxModel(pathStr, {0.485 * 255, 0.456 * 255, 0.406 * 255}, {1.0 / 0.229 / 255.0, 1.0 / 0.224 / 255.0, 1.0 / 0.225 / 255.0}, numOfThread)
    {
    }
    std::vector<TextBox> getTextBoxes(const cv::Mat &src, ScaleParam &s, float boxScoreThresh,
                                      float boxThresh, float unClipRatio);
};

class OcrLite
{
public:
    OcrLite(const std::wstring &detPath,
            const std::wstring &recPath, const std::wstring &keysPath, int numOfThread) : crnnNet(recPath, keysPath, numOfThread), dbNet(detPath, numOfThread)
    {
    }

    std::vector<TextBlock> detect(const cv::Mat &src, // const void *binptr, size_t size,
                                  int padding,
                                  float boxScoreThresh, float boxThresh, float unClipRatio, Directional);

private:
    DbNet dbNet;
    CrnnNet crnnNet;

    std::vector<cv::Mat> getPartImages(const cv::Mat &src, std::vector<TextBox> &textBoxes, Directional mode);

    std::vector<TextBlock> detect_internal(const cv::Mat &src, const int &padding, ScaleParam &scale,
                                           float boxScoreThresh = 0.6f, float boxThresh = 0.3f,
                                           float unClipRatio = 2.0f, Directional mode = Directional::H);
};