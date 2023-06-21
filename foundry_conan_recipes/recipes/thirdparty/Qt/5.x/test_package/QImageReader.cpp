#include "QCoreApplication"
#include "QImageReader"
#include <iostream>

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);

    QList<QByteArray> imageFormats = QImageReader::supportedImageFormats();
    std::cout << "Supported image format plugins:" << std::endl;
    for (int i = 0; i < imageFormats.count(); ++i)
    {
        std::cout << "\t" << qPrintable(imageFormats[i]) << std::endl;
    }

    const QList<QByteArray> requiredFormats = {
        "png",
        "jpeg",
        "gif",
        "tiff"
    };

    for (int i = 0; i < requiredFormats.count(); ++i)
    {
        const QByteArray &reqFormat = requiredFormats[i];
        if (!imageFormats.contains(reqFormat))
        {
            std::cerr << "Image format '" << qPrintable(reqFormat) << "' not supported by Qt image plugins." << std::endl;
            return -1;
        }
    }

    return 0;
}
