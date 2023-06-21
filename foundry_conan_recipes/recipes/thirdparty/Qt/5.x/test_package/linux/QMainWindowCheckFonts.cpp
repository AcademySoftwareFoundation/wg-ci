#include "QApplication"
#include "QMainWindow"
#include "QMenuBar"
#include "QStatusBar"
#include "QTimer"

#include <fstream>

#include <fcntl.h>
#include <unistd.h>

const char logfile_name[]="QMainWindow.log";

/**
 * Qt applications seems to use stderr also, not just C++ std::cerr to log some information.
 * Also <a href="https://doc.qt.io/qt-5.12/qtglobal.html#qInstallMessageHandler"/> does not seem to redirect what I need.
 */
class stderr_redirect_to_log {
public:
    stderr_redirect_to_log()
    : fd(::open(logfile_name, O_WRONLY|O_CREAT|O_TRUNC, 0660)) {
        if (fd==0) {
            throw std::runtime_error("Failed to open log file.");
        }
        const int ret=::dup2(fd, 2);    // Redirect stderr...
        if (ret==0) {
            throw std::runtime_error("Failed to redirect stderr.");
        }
    }
    ~stderr_redirect_to_log() {
        ::close(fd);
    }

    std::size_t size() const {
        std::fstream logfile(logfile_name);
        std::vector<std::string> data;
        for (std::string line; std::getline(logfile, line); ) {
            std::getline(logfile, line);
            data.emplace_back(line);
        }
        return data.size();
    }

private:
    int fd;
};

int main(int argc, char *argv[]) {
    auto test=[](int argc, char *argv[]) {
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
    };

    const stderr_redirect_to_log redirector;
    const auto app_ret=test(argc, argv);
    if (app_ret==0) {
        // Check that no messages have been logged to stderr: if there are messages, then it is likely that QFontDatabase is not correctly initialised and text may not appear in the dialogs created & in QML.
        return redirector.size()<=1 ? 0 : -1;
    }
    return app_ret;
}
