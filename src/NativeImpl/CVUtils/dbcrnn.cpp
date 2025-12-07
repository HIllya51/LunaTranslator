#include "dbcrnn.hpp"
#include <clipper2/clipper.h>
ScaleParam getScaleParam(const cv::Mat &src, const int targetSize)
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

TextBox getBox(const cv::RotatedRect &rect)
{
    TextBox vertices;
    rect.points(vertices.data());
    return vertices;
}
std::tuple<float, float, float, float> TextBox2XYXY(const TextBox &box)
{
    float collectX[4] = {box[0].x, box[1].x, box[2].x, box[3].x};
    float collectY[4] = {box[0].y, box[1].y, box[2].y, box[3].y};
    float left = *std::min_element(collectX, collectX + 4);
    float right = *std::max_element(collectX, collectX + 4);
    float top = *std::min_element(collectY, collectY + 4);
    float bottom = *std::max_element(collectY, collectY + 4);
    return std::make_tuple(left, top, right, bottom);
}
cv::Mat getRotateCropImage(const cv::Mat &src, const TextBox &box, Directional mode)
{
    cv::Mat image;
    src.copyTo(image);
    TextBox points = box;
    auto &&[left, top, right, bottom] = TextBox2XYXY(box);

    cv::Mat imgCrop;
    image(cv::Rect(left, top, right - left, bottom - top)).copyTo(imgCrop);

    for (auto &point : points)
    {
        point.x -= left;
        point.y -= top;
    }

    float imgCropWidth = sqrt(pow(points[0].x - points[1].x, 2) +
                              pow(points[0].y - points[1].y, 2));
    float imgCropHeight = sqrt(pow(points[0].x - points[3].x, 2) +
                               pow(points[0].y - points[3].y, 2));

    TextBox ptsDst;
    ptsDst[0] = cv::Point2f(0., 0.);
    ptsDst[1] = cv::Point2f(imgCropWidth, 0.);
    ptsDst[2] = cv::Point2f(imgCropWidth, imgCropHeight);
    ptsDst[3] = cv::Point2f(0.f, imgCropHeight);

    cv::Mat M = cv::getPerspectiveTransform(points.data(), ptsDst.data());

    cv::Mat partImg;
    cv::warpPerspective(imgCrop, partImg, M,
                        cv::Size(imgCropWidth, imgCropHeight),
                        cv::BORDER_REPLICATE);

    if (mode == Directional::V || (mode == Directional::Auto && (float(partImg.rows) >= float(partImg.cols) * 1.5)))
    {
        cv::transpose(partImg, partImg);
        cv::flip(partImg, partImg, 0);
    }

    return partImg;
}

bool cvPointCompare(const cv::Point &a, const cv::Point &b)
{
    return a.x < b.x;
}

TextBox getMinBoxes(const cv::RotatedRect &boxRect, float &maxSideLen)
{
    maxSideLen = std::max(boxRect.size.width, boxRect.size.height);
    TextBox boxPoint = getBox(boxRect);
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
    TextBox minBox;
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
float boxScoreFast(const TextBox &boxes, const cv::Mat &pred)
{
    int width = pred.cols;
    int height = pred.rows;

    auto &&[left, top, right, bottom] = TextBox2XYXY(boxes);
    int minX = clamp(int(std::floor(left)), 0, width - 1);
    int maxX = clamp(int(std::ceil(right)), 0, width - 1);
    int minY = clamp(int(std::floor(top)), 0, height - 1);
    int maxY = clamp(int(std::ceil(bottom)), 0, height - 1);

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

float getContourArea(const TextBox &box, float unClipRatio)
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

cv::RotatedRect unClip(const TextBox &box, float unClipRatio)
{
    float distance = getContourArea(box, unClipRatio);

    Clipper2Lib::ClipperOffset offset;
    Clipper2Lib::Path64 p;
    for (const auto &_p : box)
    {
        p.emplace_back(Clipper2Lib::Point64(int(_p.x), int(_p.y)));
    }
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
CrnnNet::CrnnNet(const std::wstring &pathStr, const std::wstring &keysPath, int numOfThread, bool gpu, int device) : CommonOnnxModel(pathStr, {127.5, 127.5, 127.5}, {1.0 / 127.5, 1.0 / 127.5, 1.0 / 127.5}, numOfThread, gpu, device)
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
    // std::vector<float> scores;
    size_t lastIndex = 0;
    size_t maxIndex;
    // float maxValue;

    for (size_t i = 0; i < h; i++)
    {
        size_t start = i * w;
        size_t stop = (i + 1) * w;
        if (stop > dataSize - 1)
        {
            stop = (i + 1) * w - 1;
        }
        maxIndex = int(argmax(&outputData[start], &outputData[stop]));
        // maxValue = float(*std::max_element(&outputData[start], &outputData[stop]));

        if (maxIndex > 0 && maxIndex < keySize && (!(i > 0 && maxIndex == lastIndex)))
        {
            // scores.emplace_back(maxValue);
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

std::vector<TextLine> CrnnNet::getTextLines(const std::vector<cv::Mat> &partImg)
{
    int size = partImg.size();
    std::vector<TextLine> textLines(size);
    for (int i = 0; i < size; ++i)
    {
        try
        {
            TextLine textLine = getTextLine(partImg[i]);
            textLines[i] = textLine;
        }
        catch (...)
        {
        }
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
        TextBox minBoxes = getMinBoxes(minAreaRect, longSide);

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

        TextBox clipMinBoxes = getMinBoxes(clipRect, longSide);
        if (longSide < longSideThresh + 2)
            continue;

        TextBox intClipMinBoxes;
        int idx = 0;
        for (auto &clipMinBox : clipMinBoxes)
        {
            float x = clipMinBox.x / s.ratioWidth;
            float y = clipMinBox.y / s.ratioHeight;
            int ptX = (std::min)((std::max)(int(x), 0), s.srcWidth - 1);
            int ptY = (std::min)((std::max)(int(y), 0), s.srcHeight - 1);
            cv::Point point{ptX, ptY};
            intClipMinBoxes[idx++] = point;
        }
        rsBoxes.push_back(intClipMinBoxes);
    }
    reverse(rsBoxes.begin(), rsBoxes.end());
    return rsBoxes;
}

std::vector<TextBox> DbNet::getTextBoxes(const cv::Mat &src, ScaleParam &s, float boxScoreThresh, float boxThresh, float unClipRatio)
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

cv::Mat makePadding(const cv::Mat &src, const int padding)
{
    if (padding <= 0)
        return src;
    cv::Scalar paddingScalar = {255, 255, 255};
    cv::Mat paddingSrc;
    cv::copyMakeBorder(src, paddingSrc, padding, padding, padding, padding, cv::BORDER_ISOLATED, paddingScalar);
    return paddingSrc;
}
std::vector<TextBlock> OcrLite::detect(const cv::Mat &src, // const void *binptr, size_t size,
                                       Directional mode,
                                       int padding,
                                       float boxScoreThresh, float boxThresh, float unClipRatio)
{
    int originMaxSide = std::max(src.cols, src.rows);
    int resize = originMaxSide;
    resize += 2 * padding;
    cv::Mat paddingSrc = makePadding(src, padding);
    ScaleParam scale = getScaleParam(paddingSrc, resize);
    return detect_internal(paddingSrc, padding, scale,
                           boxScoreThresh, boxThresh, unClipRatio, mode);
}

std::vector<cv::Mat> OcrLite::getPartImages(const cv::Mat &src, std::vector<TextBox> &textBoxes, Directional mode)
{
    std::vector<cv::Mat> partImages;
    for (size_t i = 0; i < textBoxes.size(); ++i)
    {
        cv::Mat partImg = getRotateCropImage(src, textBoxes[i], mode);
        partImages.emplace_back(partImg);
    }
    return partImages;
}

std::vector<TextBlock> OcrLite::detect_internal(const cv::Mat &src, const int &padding, ScaleParam &scale,
                                                float boxScoreThresh, float boxThresh, float unClipRatio, Directional mode)
{

    std::vector<TextBox> textBoxes = dbNet.getTextBoxes(src, scale, boxScoreThresh, boxThresh, unClipRatio);
    std::vector<cv::Mat> partImages = getPartImages(src, textBoxes, mode);

    std::vector<TextLine> textLines = crnnNet.getTextLines(partImages);

    std::vector<TextBlock> textBlocks;
    for (size_t i = 0; i < textLines.size(); ++i)
    {
        for (auto &p : textBoxes[i])
        {
            p.x -= padding;
            p.y -= padding;
        }
        TextBlock textBlock{textBoxes[i], textLines[i]};
        textBlocks.emplace_back(textBlock);
    }

    return textBlocks;
}