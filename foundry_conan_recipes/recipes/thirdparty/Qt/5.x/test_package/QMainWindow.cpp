#include "QApplication"
#include "QMainWindow"
#include "QMenuBar"
#include "QStatusBar"
#include "QTimer"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    QMainWindow wnd;
    wnd.setWindowTitle(QMainWindow::tr("A main window..."));
    wnd.menuBar()->addMenu(QMainWindow::tr("&File"));
    wnd.statusBar()->showMessage(QMainWindow::tr("A status bar..."));
    QAction* const aboutQtAction(wnd.menuBar()->addAction(QMainWindow::tr("About &Qt")));
    aboutQtAction->setMenuRole(QAction::AboutQtRole);
    QMainWindow::connect(aboutQtAction, &QAction::triggered, qApp, &QApplication::aboutQt);
    wnd.show();
    QTimer::singleShot(TIMEOUT, &app, SLOT(quit()));
    return app.exec();
}
