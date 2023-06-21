#include "QFuture"
#include "QtConcurrent"

#include <iostream>

int main(int argc, char *argv[]) {
    try {
        bool flag=false;
        auto await=QtConcurrent::run(
            [&flag]() {
                return !flag;
            }
        );
        bool res=static_cast<bool>(await);
        return res==flag ? -3 : 0;
    } catch (std::exception const &ex) {
        std::cerr<<"STL-derived exception caught. Details: "<<ex.what()<<std::endl;
        return -1;
    } catch (...) {
        std::cerr<<"Unknown exception caught."<<std::endl;
        return -2;
    }
}
