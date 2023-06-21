#include "QML_BackEnd.hpp"

BackEnd::BackEnd(QObject *parent)
: QObject(parent), m_userName("ANOther") {
}

const QString& BackEnd::userName() const {
    return m_userName;
}

void BackEnd::setUserName(const QString &userName) {
    if (userName == m_userName) {
        return;
    }
    m_userName = userName;
    emit userNameChanged();
}
