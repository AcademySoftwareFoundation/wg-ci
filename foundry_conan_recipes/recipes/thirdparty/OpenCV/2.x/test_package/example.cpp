#include <iostream>

#include "opencv/cv.h"

int main()
{
    const int width = 100;
    const int height = 100;
    const int type = CV_32F;

    cv::Mat src = cv::Mat::eye(height, width, type);
    cv::Mat dst = cv::Mat::zeros(height * 2, width * 2, type);

    // Check ones in diagonal only.
    for (int r = 0; r < src.rows; ++r)
    {
        const float* const row = reinterpret_cast<const float*>(src.ptr(r));
        for (int c = 0; c < src.cols; ++c)
        {
            const float pixel = row[c];
            if ((r == c && pixel != 1.0f) || (r != c && pixel != 0.0f))
            {
                std::cerr << "Expected ones in diagonal; rest should be zeros."
                          << std::endl;
                return 1;
            }
        }
    }

    // Check all zeros.
    for (int r = 0; r < dst.rows; ++r)
    {
        const float* const row = reinterpret_cast<const float*>(dst.ptr(r));
        for (int c = 0; c < dst.cols; ++c)
        {
            const float pixel = row[c];
            if (pixel != 0.0f)
            {
                std::cerr << "Expected only zeros in destination." << std::endl;
                return 1;
            }
        }
    }

    cv::resize(src, dst, dst.size(), 0.0, 0.0, cv::INTER_NEAREST);

    // Check ones are still intact in the diagonal after resizing.
    for (int r = 0; r < dst.rows; ++r)
    {
        const float* const row = reinterpret_cast<const float*>(dst.ptr(r));
        for (int c = 0; c < dst.cols; ++c)
        {
            const float pixel = row[c];
            if (r == c && pixel != 1.0f)
            {
                std::cerr << "Expected ones in diagonal." << std::endl;
                return 1;
            }
        }
    }

    return 0;
}
