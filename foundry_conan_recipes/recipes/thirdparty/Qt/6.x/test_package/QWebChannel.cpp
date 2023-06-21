#include <QWebChannel>

struct Test : QObject {
};

int main(int argc, char* argv[]) {
    QWebChannel channel;
    channel.registerObject(QStringLiteral("tqbfjotld"), new Test);
    return 0;
}
