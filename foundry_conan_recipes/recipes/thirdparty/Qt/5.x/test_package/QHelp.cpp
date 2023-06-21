#include "QCoreApplication"
#include "QHelpEngineCore"
#include "QTimer"

#include <string>

int main(int argc, char * argv[]) {
    const char collection_file[]="QHelp.data";
    QCoreApplication app(argc, argv);
    QHelpEngineCore help(collection_file);
    QTimer::singleShot(TIMEOUT, &app, SLOT(quit()));
    if (help.collectionFile().toStdString().find(collection_file)==std::string::npos) {
        return -1;
    }
    if (!help.setupData()) {
        return -2;
    }
    return app.exec();
}
