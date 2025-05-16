#include "format.hpp"
using namespace cv;

DECLARE_API cv::Mat *cvMatFromRGB888(const void *ptr, int width, int height, int bytesPerLine)
{
    return __cvMatFromRGB888(ptr, width, height, bytesPerLine).release();
}
DECLARE_API cv::Mat *cvMatFromBGR888(const void *ptr, int width, int height, int bytesPerLine)
{
    return __cvMatFromBGR888(ptr, width, height, bytesPerLine).release();
}
DECLARE_API void cvMatDestroy(cv::Mat *mat)
{
    if (mat)
        delete mat;
}
// https://docs.opencv.org/4.x/dd/d3d/tutorial_gpu_basics_similarity.html
// https://docs.opencv.org/3.4/d8/dc8/tutorial_histogram_comparison.html

DECLARE_API double cvMatMSSIM(const cv::Mat *mat_1, const cv::Mat *mat_2)
{
    if (!mat_1 || !mat_2)
        return 0;
    if (mat_1->size() != mat_2->size())
        return 0;
    const double C1 = 6.5025, C2 = 58.5225;
    /***************************** INITS **********************************/
    int d = CV_32F;

    Mat I1, I2;
    mat_1->convertTo(I1, d); // cannot calculate on one byte large values
    mat_2->convertTo(I2, d);

    std::vector<Mat> vI1, vI2;
    split(I1, vI1);
    split(I2, vI2);

    double mssim = 0.0;
    int channels = I1.channels();

    for (int c = 0; c < channels; c++)
    {
        Mat I1_c = vI1[c];
        Mat I2_c = vI2[c];

        Mat I2_2 = I2_c.mul(I2_c);  // I2^2
        Mat I1_2 = I1_c.mul(I1_c);  // I1^2
        Mat I1_I2 = I1_c.mul(I2_c); // I1 * I2

        /*************************** END INITS **********************************/

        Mat mu1, mu2; // PRELIMINARY COMPUTING
        GaussianBlur(I1_c, mu1, Size(11, 11), 1.5);
        GaussianBlur(I2_c, mu2, Size(11, 11), 1.5);

        Mat mu1_2 = mu1.mul(mu1);
        Mat mu2_2 = mu2.mul(mu2);
        Mat mu1_mu2 = mu1.mul(mu2);

        Mat sigma1_2, sigma2_2, sigma12;

        GaussianBlur(I1_2, sigma1_2, Size(11, 11), 1.5);
        subtract(sigma1_2, mu1_2, sigma1_2);

        GaussianBlur(I2_2, sigma2_2, Size(11, 11), 1.5);
        subtract(sigma2_2, mu2_2, sigma2_2);

        GaussianBlur(I1_I2, sigma12, Size(11, 11), 1.5);
        subtract(sigma12, mu1_mu2, sigma12);

        Mat t1, t2, t3;

        t1 = 2 * mu1_mu2 + C1;
        t2 = 2 * sigma12 + C2;
        t3 = t1.mul(t2); // t3 = ((2*mu1_mu2 + C1).*(2*sigma12 + C2))

        t1 = mu1_2 + mu2_2 + C1;
        t2 = sigma1_2 + sigma2_2 + C2;
        t1 = t1.mul(t2); // t1 =((mu1_2 + mu2_2 + C1).*(sigma1_2 + sigma2_2 + C2))

        Mat ssim_map;
        divide(t3, t1, ssim_map); // ssim_map =  t3./t1;

        Scalar channel_mssim = mean(ssim_map);
        double channel_weight = (channels == 3) ? (c == 0 ? 0.299 : (c == 1 ? 0.587 : 0.114)) : 1.0;
        mssim += channel_weight * channel_mssim[0];
    }

    return mssim;
}