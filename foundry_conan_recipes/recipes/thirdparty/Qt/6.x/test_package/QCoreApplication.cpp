#include "QCoreApplication"
#include "QTimer"

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);
    QTimer::singleShot(TIMEOUT, &app, SLOT(quit()));
    return app.exec();
}
