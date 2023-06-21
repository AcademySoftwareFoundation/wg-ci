/**
    \file Example is taken from https://code.qt.io/cgit/qt/qtsvg.git/tree/examples/svg/svgviewer/
*/

#include "QApplication"
#include "QGraphicsSvgItem"
#include "QGraphicsView"
#include "QMainWindow"
#include "QSvgRenderer"
#include "QTimer"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    QMainWindow wnd;
    QGraphicsSvgItem svgItem(SVG_IMAGE_FILEPATH);
    if (!svgItem.renderer()->isValid()) {
        return -1;
    }
    svgItem.setFlags(QGraphicsItem::ItemClipsToShape);
    svgItem.setCacheMode(QGraphicsItem::NoCache);
    svgItem.setZValue(0);
    QGraphicsView *view=new QGraphicsView;
    wnd.setCentralWidget(view);
    view->setViewport(new QWidget);
    view->setScene(new QGraphicsScene(view));
    QGraphicsScene * const s=view->scene();
    if (s==nullptr) {
        return -2;
    }
    s->addItem(&svgItem);
    s->setSceneRect(svgItem.boundingRect().adjusted(-10, -10, 10, 10));
    QTimer::singleShot(TIMEOUT, &app, SLOT(quit()));
    wnd.show();
    return app.exec();
}
