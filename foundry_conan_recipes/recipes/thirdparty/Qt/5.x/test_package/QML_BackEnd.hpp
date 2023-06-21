#include "QObject"
#include "QString"

class BackEnd : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString userName READ userName WRITE setUserName NOTIFY userNameChanged)

public:
    explicit BackEnd(QObject *parent = nullptr);

    const QString& userName() const;
    void setUserName(const QString &userName);

signals:
    void userNameChanged();

private:
    QString m_userName;
};
