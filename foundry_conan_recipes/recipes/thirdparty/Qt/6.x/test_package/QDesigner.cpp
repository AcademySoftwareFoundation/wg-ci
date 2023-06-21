#include "QExtensionFactory"

int main(int, char *[]) {
    const QExtensionFactory factory;
    return factory.extensionManager()==nullptr ? 0 : -1;
}
