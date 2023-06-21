/**
 * \file Example from <a href="https://doc.qt.io/qt-5/qtdoc-demos-calqlatr-example.html"/>.
 */

#include "QGuiApplication"
#include "QQmlEngine"
#include "QQuickView"
#include "QTimer"

#include <iostream>

int main(int argc, char *argv[]) {
    try {
        QGuiApplication app(argc, argv);
        QQuickView view;
        view.connect(view.engine(), &QQmlEngine::quit, &app, &QCoreApplication::quit);
        view.setSource(QUrl::fromLocalFile(QQuick_main_FILEPATH));
        if (view.status() == QQuickView::Error)
            return -1;
        view.setResizeMode(QQuickView::SizeRootObjectToView);
        view.show();
        QTimer::singleShot(2*TIMEOUT, &app, SLOT(quit()));
        return app.exec();
    } catch (std::exception const &ex) {
        std::cerr<<"STL-derived exception caught. Details: "<<ex.what()<<std::endl;
        return -2;
    } catch (...) {
        std::cerr<<"Unknown exception caught."<<std::endl;
        return -3;
    }
}
