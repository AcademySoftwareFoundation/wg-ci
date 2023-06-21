#include "QCoreApplication"
#include "QTimer"
#include "QX11Info"

#include <iostream>

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);
    QTimer::singleShot(TIMEOUT, &app, SLOT(quit()));
    const int screen=QX11Info::appScreen();
    if (screen!=0) {
        return -1;
    }
    return app.exec();
}
