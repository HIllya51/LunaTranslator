#include <onnxruntime_cxx_api.h>
#include <opencv2/opencv.hpp>
#include <clipper2/clipper.h>
typedef std::vector<cv::Point> TextBox;
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
#if ORT_API_VERSION <= 10
#define STRINGT const char *
#define FGetInputName GetInputName
#define FGetOutputName GetOutputName
#define GetVector(X) X
#else
#define STRINGT Ort::AllocatedStringPtr
#define FGetInputName GetInputNameAllocated
#define FGetOutputName GetOutputNameAllocated
#define GetVector(X) {X.data()->get()}
#endif
class CommonOnnxModel
{
    std::vector<STRINGT> inputNamesPtr;
    std::vector<STRINGT> outputNamesPtr;
    std::unique_ptr<Ort::Session> session;
    Ort::Env env = Ort::Env(ORT_LOGGING_LEVEL_ERROR);
    Ort::SessionOptions sessionOptions = Ort::SessionOptions();
    const std::array<float, 3> meanValues;
    const std::array<float, 3> normValues;

    std::vector<float> substractMeanNormalize(cv::Mat &src, const float *meanVals, const float *normVals)
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

    void setNumThread(int numOfThread)
    {
        sessionOptions.SetInterOpNumThreads(numOfThread);
        sessionOptions.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_EXTENDED);
    }

    template <typename T, typename Func, typename Func2>
    void getinputoutputNames(T &vec, Func func, Func2 func2)
    {
        Ort::AllocatorWithDefaultOptions allocator;
        const size_t numInputNodes = ((*session.get()).*func)();
        vec.reserve(numInputNodes);
        std::vector<int64_t> input_node_dims;

        for (size_t i = 0; i < numInputNodes; i++)
        {
            auto inputName = ((*session.get()).*func2)(i, allocator);
            vec.push_back(std::move(inputName));
        }
    }

public:
    std::pair<std::vector<float>, std::vector<int64_t>> RunSession(cv::Mat src)
    {
        auto inputTensorValues = substractMeanNormalize(src, meanValues.data(), normValues.data());
        std::array<int64_t, 4> inputShape{1, src.channels(), src.rows, src.cols};
        auto memoryInfo = Ort::MemoryInfo::CreateCpu(OrtDeviceAllocator, OrtMemTypeCPU);
        Ort::Value inputTensor = Ort::Value::CreateTensor<float>(memoryInfo, inputTensorValues.data(),
                                                                 inputTensorValues.size(), inputShape.data(),
                                                                 inputShape.size());
        assert(inputTensor.IsTensor());
        std::vector<const char *> inputNames = GetVector(inputNamesPtr);
        std::vector<const char *> outputNames = GetVector(outputNamesPtr);
        auto outputTensor = session->Run(Ort::RunOptions{nullptr}, inputNames.data(), &inputTensor,
                                         inputNames.size(), outputNames.data(), outputNames.size());
        assert(outputTensor.size() == 1 && outputTensor.front().IsTensor());
        std::vector<int64_t> outputShape = outputTensor[0].GetTensorTypeAndShapeInfo().GetShape();
        auto outputCount = outputTensor.front().GetTensorTypeAndShapeInfo().GetElementCount();
        float *floatArray = outputTensor.front().GetTensorMutableData<float>();
        std::vector<float> outputData(floatArray, floatArray + outputCount);
        return {outputData, outputShape};
    }
    CommonOnnxModel(const std::wstring &path, const std::array<float, 3> &_meanValues, const std::array<float, 3> &_normValues, int numOfThread = 4) : meanValues(_meanValues), normValues(_normValues)
    {
        setNumThread(numOfThread);
        session = std::make_unique<Ort::Session>(env, path.c_str(), sessionOptions);
        getinputoutputNames(inputNamesPtr, &Ort::Session::GetInputCount, &Ort::Session::FGetInputName);
        getinputoutputNames(outputNamesPtr, &Ort::Session::GetOutputCount, &Ort::Session::FGetOutputName);
    }
};

class CrnnNet : public CommonOnnxModel
{
public:
    CrnnNet(const std::wstring &pathStr, const std::wstring &keysPath, int numOfThread);
    std::vector<TextLine> getTextLines(std::vector<cv::Mat> &partImg);

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
    std::vector<TextBox> getTextBoxes(cv::Mat &src, ScaleParam &s, float boxScoreThresh,
                                      float boxThresh, float unClipRatio);
};

// onnxruntime init windows
ScaleParam getScaleParam(cv::Mat &src, const float scale)
{
    int srcWidth = src.cols;
    int srcHeight = src.rows;
    int dstWidth = int((float)srcWidth * scale);
    int dstHeight = int((float)srcHeight * scale);
    if (dstWidth % 32 != 0)
    {
        dstWidth = (dstWidth / 32 - 1) * 32;
        dstWidth = (std::max)(dstWidth, 32);
    }
    if (dstHeight % 32 != 0)
    {
        dstHeight = (dstHeight / 32 - 1) * 32;
        dstHeight = (std::max)(dstHeight, 32);
    }
    float scaleWidth = (float)dstWidth / (float)srcWidth;
    float scaleHeight = (float)dstHeight / (float)srcHeight;
    return {srcWidth, srcHeight, dstWidth, dstHeight, scaleWidth, scaleHeight};
}

ScaleParam getScaleParam(cv::Mat &src, const int targetSize)
{
    int srcWidth, srcHeight, dstWidth, dstHeight;
    srcWidth = dstWidth = src.cols;
    srcHeight = dstHeight = src.rows;

    float ratio = 1.f;
    if (srcWidth > srcHeight)
    {
        ratio = float(targetSize) / float(srcWidth);
    }
    else
    {
        ratio = float(targetSize) / float(srcHeight);
    }
    dstWidth = int(float(srcWidth) * ratio);
    dstHeight = int(float(srcHeight) * ratio);
    if (dstWidth % 32 != 0)
    {
        dstWidth = (dstWidth / 32) * 32;
        dstWidth = (std::max)(dstWidth, 32);
    }
    if (dstHeight % 32 != 0)
    {
        dstHeight = (dstHeight / 32) * 32;
        dstHeight = (std::max)(dstHeight, 32);
    }
    float ratioWidth = (float)dstWidth / (float)srcWidth;
    float ratioHeight = (float)dstHeight / (float)srcHeight;
    return {srcWidth, srcHeight, dstWidth, dstHeight, ratioWidth, ratioHeight};
}

std::vector<cv::Point2f> getBox(const cv::RotatedRect &rect)
{
    cv::Point2f vertices[4];
    rect.points(vertices);
    // std::vector<cv::Point2f> ret(4);
    std::vector<cv::Point2f> ret2(vertices, vertices + sizeof(vertices) / sizeof(vertices[0]));
    // memcpy(vertices, &ret[0], ret.size() * sizeof(ret[0]));
    return ret2;
}

cv::Mat getRotateCropImage(const cv::Mat &src, std::vector<cv::Point> box)
{
    cv::Mat image;
    src.copyTo(image);
    std::vector<cv::Point> points = box;

    int collectX[4] = {box[0].x, box[1].x, box[2].x, box[3].x};
    int collectY[4] = {box[0].y, box[1].y, box[2].y, box[3].y};
    int left = int(*std::min_element(collectX, collectX + 4));
    int right = int(*std::max_element(collectX, collectX + 4));
    int top = int(*std::min_element(collectY, collectY + 4));
    int bottom = int(*std::max_element(collectY, collectY + 4));

    cv::Mat imgCrop;
    image(cv::Rect(left, top, right - left, bottom - top)).copyTo(imgCrop);

    for (auto &point : points)
    {
        point.x -= left;
        point.y -= top;
    }

    int imgCropWidth = int(sqrt(pow(points[0].x - points[1].x, 2) +
                                pow(points[0].y - points[1].y, 2)));
    int imgCropHeight = int(sqrt(pow(points[0].x - points[3].x, 2) +
                                 pow(points[0].y - points[3].y, 2)));

    cv::Point2f ptsDst[4];
    ptsDst[0] = cv::Point2f(0., 0.);
    ptsDst[1] = cv::Point2f(imgCropWidth, 0.);
    ptsDst[2] = cv::Point2f(imgCropWidth, imgCropHeight);
    ptsDst[3] = cv::Point2f(0.f, imgCropHeight);

    cv::Point2f ptsSrc[4];
    ptsSrc[0] = cv::Point2f(points[0].x, points[0].y);
    ptsSrc[1] = cv::Point2f(points[1].x, points[1].y);
    ptsSrc[2] = cv::Point2f(points[2].x, points[2].y);
    ptsSrc[3] = cv::Point2f(points[3].x, points[3].y);

    cv::Mat M = cv::getPerspectiveTransform(ptsSrc, ptsDst);

    cv::Mat partImg;
    cv::warpPerspective(imgCrop, partImg, M,
                        cv::Size(imgCropWidth, imgCropHeight),
                        cv::BORDER_REPLICATE);

    // if (float(partImg.rows) >= float(partImg.cols) * 1.5) {
    //     cv::Mat srcCopy = cv::Mat(partImg.rows, partImg.cols, partImg.depth());
    //     cv::transpose(partImg, srcCopy);
    //     cv::flip(srcCopy, srcCopy, 0);
    //     return srcCopy;
    // } else {
    //     return partImg;
    // }

    return partImg;
}

bool cvPointCompare(const cv::Point &a, const cv::Point &b)
{
    return a.x < b.x;
}

std::vector<cv::Point2f> getMinBoxes(const cv::RotatedRect &boxRect, float &maxSideLen)
{
    maxSideLen = std::max(boxRect.size.width, boxRect.size.height);
    std::vector<cv::Point2f> boxPoint = getBox(boxRect);
    std::sort(boxPoint.begin(), boxPoint.end(), cvPointCompare);
    int index1, index2, index3, index4;
    if (boxPoint[1].y > boxPoint[0].y)
    {
        index1 = 0;
        index4 = 1;
    }
    else
    {
        index1 = 1;
        index4 = 0;
    }
    if (boxPoint[3].y > boxPoint[2].y)
    {
        index2 = 2;
        index3 = 3;
    }
    else
    {
        index2 = 3;
        index3 = 2;
    }
    std::vector<cv::Point2f> minBox(4);
    minBox[0] = boxPoint[index1];
    minBox[1] = boxPoint[index2];
    minBox[2] = boxPoint[index3];
    minBox[3] = boxPoint[index4];
    return minBox;
}

template <class T>
inline T clamp(T x, T min, T max)
{
    if (x > max)
        return max;
    if (x < min)
        return min;
    return x;
}
float boxScoreFast(const std::vector<cv::Point2f> &boxes, const cv::Mat &pred)
{
    int width = pred.cols;
    int height = pred.rows;

    float arrayX[4] = {boxes[0].x, boxes[1].x, boxes[2].x, boxes[3].x};
    float arrayY[4] = {boxes[0].y, boxes[1].y, boxes[2].y, boxes[3].y};

    int minX = clamp(int(std::floor(*(std::min_element(arrayX, arrayX + 4)))), 0, width - 1);
    int maxX = clamp(int(std::ceil(*(std::max_element(arrayX, arrayX + 4)))), 0, width - 1);
    int minY = clamp(int(std::floor(*(std::min_element(arrayY, arrayY + 4)))), 0, height - 1);
    int maxY = clamp(int(std::ceil(*(std::max_element(arrayY, arrayY + 4)))), 0, height - 1);

    cv::Mat mask = cv::Mat::zeros(maxY - minY + 1, maxX - minX + 1, CV_8UC1);

    cv::Point box[4];
    box[0] = cv::Point(int(boxes[0].x) - minX, int(boxes[0].y) - minY);
    box[1] = cv::Point(int(boxes[1].x) - minX, int(boxes[1].y) - minY);
    box[2] = cv::Point(int(boxes[2].x) - minX, int(boxes[2].y) - minY);
    box[3] = cv::Point(int(boxes[3].x) - minX, int(boxes[3].y) - minY);
    const cv::Point *pts[1] = {box};
    int npts[] = {4};
    cv::fillPoly(mask, pts, npts, 1, cv::Scalar(1));

    cv::Mat croppedImg;
    pred(cv::Rect(minX, minY, maxX - minX + 1, maxY - minY + 1))
        .copyTo(croppedImg);

    auto score = (float)cv::mean(croppedImg, mask)[0];
    return score;
}

float getContourArea(const std::vector<cv::Point2f> &box, float unClipRatio)
{
    size_t size = box.size();
    float area = 0.0f;
    float dist = 0.0f;
    for (size_t i = 0; i < size; i++)
    {
        area += box[i].x * box[(i + 1) % size].y -
                box[i].y * box[(i + 1) % size].x;
        dist += sqrtf((box[i].x - box[(i + 1) % size].x) *
                          (box[i].x - box[(i + 1) % size].x) +
                      (box[i].y - box[(i + 1) % size].y) *
                          (box[i].y - box[(i + 1) % size].y));
    }
    area = fabs(float(area / 2.0));

    return area * unClipRatio / dist;
}

cv::RotatedRect unClip(std::vector<cv::Point2f> box, float unClipRatio)
{
    float distance = getContourArea(box, unClipRatio);

    Clipper2Lib::ClipperOffset offset;
    Clipper2Lib::Path64 p;
    p.push_back(Clipper2Lib::Point64(int(box[0].x), int(box[0].y)));
    p.push_back(Clipper2Lib::Point64(int(box[1].x), int(box[1].y)));
    p.push_back(Clipper2Lib::Point64(int(box[2].x), int(box[2].y)));
    p.push_back(Clipper2Lib::Point64(int(box[3].x), int(box[3].y)));
    offset.AddPath(p, Clipper2Lib::JoinType::Round, Clipper2Lib::EndType::Polygon);
    Clipper2Lib::Paths64 soln;
    offset.Execute(distance, soln);
    std::vector<cv::Point2f> points;

    for (size_t j = 0; j < soln.size(); j++)
    {
        for (size_t i = 0; i < soln[soln.size() - 1].size(); i++)
        {
            points.emplace_back(cv::Point2f{float(soln[j][i].x), float(soln[j][i].y)});
        }
    }
    cv::RotatedRect res;
    if (points.empty())
    {
        res = cv::RotatedRect(cv::Point2f(0, 0), cv::Size2f(1, 1), 0);
    }
    else
    {
        res = cv::minAreaRect(points);
    }
    return res;
}
CrnnNet::CrnnNet(const std::wstring &pathStr, const std::wstring &keysPath, int numOfThread) : CommonOnnxModel(pathStr, {127.5, 127.5, 127.5}, {1.0 / 127.5, 1.0 / 127.5, 1.0 / 127.5}, numOfThread)
{
    // load keys
    std::ifstream in(keysPath.c_str());
    std::string line;
    if (in)
    {
        while (getline(in, line))
        { // line中不包括每行的换行符
            keys.push_back(line);
        }
    }
    else
    {
        return;
    }
    keys.insert(keys.begin(), "#");
    keys.emplace_back(" ");
}

template <class ForwardIterator>
inline static size_t argmax(ForwardIterator first, ForwardIterator last)
{
    return std::distance(first, std::max_element(first, last));
}

TextLine CrnnNet::scoreToTextLine(const std::vector<float> &outputData, size_t h, size_t w)
{
    auto keySize = keys.size();
    auto dataSize = outputData.size();
    std::string strRes;
    std::vector<float> scores;
    size_t lastIndex = 0;
    size_t maxIndex;
    float maxValue;

    for (size_t i = 0; i < h; i++)
    {
        size_t start = i * w;
        size_t stop = (i + 1) * w;
        if (stop > dataSize - 1)
        {
            stop = (i + 1) * w - 1;
        }
        maxIndex = int(argmax(&outputData[start], &outputData[stop]));
        maxValue = float(*std::max_element(&outputData[start], &outputData[stop]));

        if (maxIndex > 0 && maxIndex < keySize && (!(i > 0 && maxIndex == lastIndex)))
        {
            scores.emplace_back(maxValue);
            strRes.append(keys[maxIndex]);
        }
        lastIndex = maxIndex;
    }
    return strRes;
}

TextLine CrnnNet::getTextLine(const cv::Mat &src)
{
    float scale = (float)dstHeight / (float)src.rows;
    int dstWidth = int((float)src.cols * scale);
    cv::Mat srcResize;
    resize(src, srcResize, cv::Size(dstWidth, dstHeight));
    auto &&[outputData, outputShape] = RunSession(srcResize);
    return scoreToTextLine(outputData, outputShape[1], outputShape[2]);
}

std::vector<TextLine> CrnnNet::getTextLines(std::vector<cv::Mat> &partImg)
{
    int size = partImg.size();
    std::vector<TextLine> textLines(size);
    for (int i = 0; i < size; ++i)
    {
        TextLine textLine = getTextLine(partImg[i]);
        textLines[i] = textLine;
    }
    return textLines;
}

std::vector<TextBox> findRsBoxes(const cv::Mat &predMat, const cv::Mat &dilateMat, ScaleParam &s,
                                 const float boxScoreThresh, const float unClipRatio)
{
    const int longSideThresh = 3; // minBox 长边门限
    const int maxCandidates = 1000;

    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;

    cv::findContours(dilateMat, contours, hierarchy, cv::RETR_LIST,
                     cv::CHAIN_APPROX_SIMPLE);

    size_t numContours = contours.size() >= maxCandidates ? maxCandidates : contours.size();

    std::vector<TextBox> rsBoxes;

    for (size_t i = 0; i < numContours; i++)
    {
        if (contours[i].size() <= 2)
        {
            continue;
        }
        cv::RotatedRect minAreaRect = cv::minAreaRect(contours[i]);

        float longSide;
        std::vector<cv::Point2f> minBoxes = getMinBoxes(minAreaRect, longSide);

        if (longSide < longSideThresh)
        {
            continue;
        }

        float boxScore = boxScoreFast(minBoxes, predMat);
        if (boxScore < boxScoreThresh)
            continue;

        //-----unClip-----
        cv::RotatedRect clipRect = unClip(minBoxes, unClipRatio);
        if (clipRect.size.height < 1.001 && clipRect.size.width < 1.001)
        {
            continue;
        }
        //-----unClip-----

        std::vector<cv::Point2f> clipMinBoxes = getMinBoxes(clipRect, longSide);
        if (longSide < longSideThresh + 2)
            continue;

        std::vector<cv::Point> intClipMinBoxes;

        for (auto &clipMinBox : clipMinBoxes)
        {
            float x = clipMinBox.x / s.ratioWidth;
            float y = clipMinBox.y / s.ratioHeight;
            int ptX = (std::min)((std::max)(int(x), 0), s.srcWidth - 1);
            int ptY = (std::min)((std::max)(int(y), 0), s.srcHeight - 1);
            cv::Point point{ptX, ptY};
            intClipMinBoxes.push_back(point);
        }
        rsBoxes.push_back(intClipMinBoxes);
    }
    reverse(rsBoxes.begin(), rsBoxes.end());
    return rsBoxes;
}

std::vector<TextBox> DbNet::getTextBoxes(cv::Mat &src, ScaleParam &s, float boxScoreThresh, float boxThresh, float unClipRatio)
{
    cv::Mat srcResize;
    resize(src, srcResize, cv::Size(s.dstWidth, s.dstHeight));
    auto &&[outputData, outputShape] = RunSession(srcResize);

    //-----Data preparation-----
    int outHeight = (int)outputShape[2];
    int outWidth = (int)outputShape[3];
    size_t area = outHeight * outWidth;

    std::vector<float> predData(area, 0.0);
    std::vector<unsigned char> cbufData(area, ' ');

    for (int i = 0; i < area; i++)
    {
        predData[i] = float(outputData[i]);
        cbufData[i] = (unsigned char)((outputData[i]) * 255);
    }

    cv::Mat predMat(outHeight, outWidth, CV_32F, (float *)predData.data());
    cv::Mat cBufMat(outHeight, outWidth, CV_8UC1, (unsigned char *)cbufData.data());

    //-----boxThresh-----
    const double maxValue = 255;
    const double threshold = boxThresh * 255;
    cv::Mat thresholdMat;
    cv::threshold(cBufMat, thresholdMat, threshold, maxValue, cv::THRESH_BINARY);

    //-----dilate-----
    cv::Mat dilateMat;
    cv::Mat dilateElement = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(2, 2));
    cv::dilate(thresholdMat, dilateMat, dilateElement);

    return findRsBoxes(predMat, dilateMat, s, boxScoreThresh, unClipRatio);
}

class OcrLite
{
public:
    OcrLite(const std::wstring &detPath,
            const std::wstring &recPath, const std::wstring &keysPath, int numOfThread) : crnnNet(recPath, keysPath, numOfThread), dbNet(detPath, numOfThread)
    {
    }

    std::vector<TextBlock> detect(const void *ptr, int width, int height, int bytesPerLine, // const void *binptr, size_t size,
                                  int padding, int maxSideLen,
                                  float boxScoreThresh, float boxThresh, float unClipRatio, Directional);

private:
    DbNet dbNet;
    CrnnNet crnnNet;

    std::vector<cv::Mat> getPartImages(cv::Mat &src, std::vector<TextBox> &textBoxes);

    std::vector<TextBlock> detect_internal(cv::Mat &src, cv::Rect &originRect, ScaleParam &scale,
                                           float boxScoreThresh = 0.6f, float boxThresh = 0.3f,
                                           float unClipRatio = 2.0f, Directional mode = Directional::H);
    bool guess_V(const std::vector<TextBox> &);
};

cv::Mat makePadding(cv::Mat &src, const int padding)
{
    if (padding <= 0)
        return src;
    cv::Scalar paddingScalar = {255, 255, 255};
    cv::Mat paddingSrc;
    cv::copyMakeBorder(src, paddingSrc, padding, padding, padding, padding, cv::BORDER_ISOLATED, paddingScalar);
    return paddingSrc;
}
namespace
{
    cv::Mat LoadMatFromBMP(const void *binptr, size_t size)
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
        auto mat = cv::Mat(height, width, (infoHeader->biBitCount == 24) ? CV_8UC3 : CV_8UC4, (void *)pixelData, rowSize);
        cv::flip(mat, mat, 0);
        return std::move(mat);
    }
    cv::Mat LoadMatFromQImageFormat_RGB888(const void *ptr, int width, int height, int bytesPerLine)
    {
        auto mat = cv::Mat(height, width, CV_8UC3, (void *)ptr, bytesPerLine);
        return std::move(mat);
    }
}
std::vector<TextBlock> OcrLite::detect(const void *ptr, int width, int height, int bytesPerLine, // const void *binptr, size_t size,
                                       const int padding,
                                       const int maxSideLen,
                                       float boxScoreThresh, float boxThresh, float unClipRatio, Directional mode)
{
    // std::vector<uchar> bytes{(uchar *)binptr, (uchar *)binptr + size};
    // cv::Mat originSrc = imdecode(bytes, cv::IMREAD_COLOR); // default : BGR
    // cv::Mat originSrc = std::move(LoadMatFromBMP(binptr, size));
    cv::Mat originSrc = std::move(LoadMatFromQImageFormat_RGB888(ptr, width, height, bytesPerLine));
    int originMaxSide = (std::max)(originSrc.cols, originSrc.rows);
    int resize;
    if (maxSideLen <= 0 || maxSideLen > originMaxSide)
    {
        resize = originMaxSide;
    }
    else
    {
        resize = maxSideLen;
    }
    resize += 2 * padding;
    cv::Rect paddingRect(padding, padding, originSrc.cols, originSrc.rows);
    cv::Mat paddingSrc = makePadding(originSrc, padding);
    ScaleParam scale = getScaleParam(paddingSrc, resize);
    return detect_internal(paddingSrc, paddingRect, scale,
                           boxScoreThresh, boxThresh, unClipRatio, mode);
}

std::vector<cv::Mat> OcrLite::getPartImages(cv::Mat &src, std::vector<TextBox> &textBoxes)
{
    std::vector<cv::Mat> partImages;
    for (size_t i = 0; i < textBoxes.size(); ++i)
    {
        cv::Mat partImg = getRotateCropImage(src, textBoxes[i]);
        partImages.emplace_back(partImg);
    }
    return partImages;
}

void matRotateClockWise180(cv::Mat &src)
{
    flip(src, src, 0);
    flip(src, src, 1);
}

void matRotateClockWise90(cv::Mat &src)
{
    transpose(src, src);
    flip(src, src, 1);
}
bool OcrLite::guess_V(const std::vector<TextBox> &textBoxes)
{
    auto whs = 1.0f;
    for (auto &box : textBoxes)
    {
        int minX = std::numeric_limits<int>::max();
        int minY = std::numeric_limits<int>::max();
        int maxX = std::numeric_limits<int>::min();
        int maxY = std::numeric_limits<int>::min();
        for (auto &point : box)
        {
            if (point.x < minX)
                minX = point.x;
            if (point.y < minY)
                minY = point.y;
            if (point.x > maxX)
                maxX = point.x;
            if (point.y > maxY)
                maxY = point.y;
        }
        auto w = maxX - minX;
        auto h = maxY - minY;
        if (h == 0 || w == 0)
            continue;
        whs *= w / h;
    }
    return whs < 1;
}
std::vector<TextBlock> OcrLite::detect_internal(cv::Mat &src, cv::Rect &originRect, ScaleParam &scale,
                                                float boxScoreThresh, float boxThresh, float unClipRatio, Directional mode)
{

    std::vector<TextBox> textBoxes = dbNet.getTextBoxes(src, scale, boxScoreThresh, boxThresh, unClipRatio);
    std::vector<cv::Mat> partImages = getPartImages(src, textBoxes);
    for (size_t i = 0; i < partImages.size(); ++i)
    {
        if (mode == Directional::V || (mode == Directional::Auto && guess_V(textBoxes)))
        {
            matRotateClockWise180(partImages[i]);
            matRotateClockWise90(partImages[i]);
        }
    }

    std::vector<TextLine> textLines = crnnNet.getTextLines(partImages);

    std::vector<TextBlock> textBlocks;
    for (size_t i = 0; i < textLines.size(); ++i)
    {
        std::vector<cv::Point> boxPoint = std::vector<cv::Point>(4);
        int padding = originRect.x; // padding conversion
        boxPoint[0] = cv::Point(textBoxes[i][0].x - padding, textBoxes[i][0].y - padding);
        boxPoint[1] = cv::Point(textBoxes[i][1].x - padding, textBoxes[i][1].y - padding);
        boxPoint[2] = cv::Point(textBoxes[i][2].x - padding, textBoxes[i][2].y - padding);
        boxPoint[3] = cv::Point(textBoxes[i][3].x - padding, textBoxes[i][3].y - padding);
        TextBlock textBlock{boxPoint, textLines[i]};
        textBlocks.emplace_back(textBlock);
    }

    return textBlocks;
}

struct ocrpoints
{
    int x1, y1, x2, y2, x3, y3, x4, y4;
};
DECLARE_API OcrLite *OcrInit(const wchar_t *szDetModel, const wchar_t *szRecModel, const wchar_t *szKeyPath, int nThreads)
{
    OcrLite *pOcrObj = nullptr;
    try
    {
        pOcrObj = new OcrLite(szDetModel, szRecModel, szKeyPath, nThreads);
    }
    catch (...)
    {
    }
    if (pOcrObj)
    {
        return pOcrObj;
    }
    else
    {
        return nullptr;
    }
}

DECLARE_API void OcrDetect(OcrLite *pOcrObj, const void *ptr, int width, int height, int bytesPerLine, // const void *binptr, size_t size,
                           Directional mode, void (*cb)(ocrpoints, const char *))
{
    if (!pOcrObj)
        return;

    try
    {
        // auto result = pOcrObj->detect(binptr, size, 50, 1024, 0.1, 0.1, 2.0, mode);
        auto result = pOcrObj->detect(ptr, width, height, bytesPerLine, 50, 1024, 0.1, 0.1, 2.0, mode);

        for (auto item : result)
        {
            cb({item.first[0].x, item.first[0].y,
                item.first[1].x, item.first[1].y,
                item.first[2].x, item.first[2].y,
                item.first[3].x, item.first[3].y},
               item.second.c_str());
        }
    }
    catch (...)
    {
    }
}

DECLARE_API void OcrDestroy(OcrLite *pOcrObj)
{
    if (pOcrObj)
        delete pOcrObj;
}
DECLARE_API void OcrListProviders()
{
    for (auto &&s : Ort::GetAvailableProviders())
    {
        std::cout << s << "\n";
    }
}