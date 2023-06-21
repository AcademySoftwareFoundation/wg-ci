#include "QSslSocket"

int main(int argc, char *argv[]) {
    QSslSocket socket;
    return QSslSocket::supportsSsl() ? 0 : -1;
}
