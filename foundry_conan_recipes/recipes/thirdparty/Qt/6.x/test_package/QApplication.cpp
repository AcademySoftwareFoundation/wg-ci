#include "QApplication"
#include "QTimer"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    QTimer::singleShot(TIMEOUT, &app, SLOT(quit()));
    return app.exec();
}
