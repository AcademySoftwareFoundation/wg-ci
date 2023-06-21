/**
 * \file Example from <a href="https://doc.qt.io/qt-5.12/qtqml-cppintegration-topic.html"/>.
 */

#include "QML_BackEnd.hpp"
#include "QML_Checker.hpp"

#include "QGuiApplication"
#include "QQmlApplicationEngine"
#include "QTimer"

#include <iostream>

int main(int argc, char *argv[]) {
    try {
        QGuiApplication app(argc, argv);
        qmlRegisterType<BackEnd>("io.qt.examples.backend", 1, 0, "BackEnd");
        QMLChecker eventLoop;
        QQmlApplicationEngine engine;
        QObject::connect(&engine, SIGNAL(objectCreated(QObject *, const QUrl &)), &eventLoop, SLOT(check(QObject *, const QUrl &)));
        engine.load(QML_main_FILEPATH);
        QTimer::singleShot(2*TIMEOUT, &app, SLOT(quit()));
        return app.exec();
    } catch (std::exception const &ex) {
        std::cerr<<"STL-derived exception caught. Details: "<<ex.what()<<std::endl;
        return -1;
    } catch (...) {
        std::cerr<<"Unknown exception caught."<<std::endl;
        return -2;
    }
}
