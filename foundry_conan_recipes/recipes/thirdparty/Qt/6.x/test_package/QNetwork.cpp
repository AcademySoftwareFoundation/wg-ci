#include "QCoreApplication"
#include "QtNetwork"
#include "QTimer"

#include <memory>

int main(int argc, char *argv[]) {
    // From: //Foundry/Packages/Thirdparty/Qt/5.12.1/work/-p1_with_test_package/test_package/test_package.cpp
    QCoreApplication app(argc, argv);

    qDebug() << "[TEST] Running test...";

    QNetworkAccessManager manager(&app);
    QEventLoop eventLoop;
    QObject::connect(&manager, SIGNAL(finished(QNetworkReply*)), &eventLoop, SLOT(quit()));
    std::unique_ptr<QNetworkReply> reply(manager.get(QNetworkRequest(QUrl("http://www.google.com"))));
    eventLoop.exec(QEventLoop::ExcludeUserInputEvents);

    // Print or catch the status code
    const QVariant status_code = reply->attribute(QNetworkRequest::HttpStatusCodeAttribute);
    const QString status = status_code.toString();
    qDebug() << "[TEST] Response code: " << status;
    if (status.isEmpty()) {
        return -1;
    }

    QTimer::singleShot(TIMEOUT, &app, SLOT(quit()));
    return app.exec();
}
