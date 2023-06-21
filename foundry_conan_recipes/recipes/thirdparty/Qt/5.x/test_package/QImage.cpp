#include "QCoreApplication"
#include "QImage"
#include <iostream>

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);
    const QImage png(PNG_IMAGE_FILEPATH, "PNG");
    if (png.isNull()) {
        std::cerr << "PNG was null: '" << PNG_IMAGE_FILEPATH << "'" << std::endl;
        return -1;
    }
    const QImage jpeg(JPEG_IMAGE_FILEPATH, "JPEG");
    if (jpeg.isNull()) {
        std::cerr << "JPEG was null: '" << JPEG_IMAGE_FILEPATH << "'" << std::endl;
        return -2;
    }
    return 0;
}
