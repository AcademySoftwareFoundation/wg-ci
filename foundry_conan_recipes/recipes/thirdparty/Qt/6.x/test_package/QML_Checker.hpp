#include "QObject"

class QMLChecker : public QObject {
    Q_OBJECT
public slots:
    void check(QObject *obj, const QUrl &url);
};
