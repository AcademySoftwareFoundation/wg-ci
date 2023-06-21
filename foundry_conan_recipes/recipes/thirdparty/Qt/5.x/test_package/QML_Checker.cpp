#include "QML_Checker.hpp"

#include "QUrl"

#include <sstream>

void QMLChecker::check(QObject *obj, const QUrl &url) {
    if (obj==nullptr) {
        std::ostringstream ss;
        ss<<"QML file '" QML_main_FILEPATH "' requested to be loaded, file '"<<url.toString().toStdString()<<"' selected. obj=0x"<<obj<<"";
        throw std::runtime_error(ss.str());
    }
}
