#include <zipstream.hpp>
#include <sstream>
#include <string>

int main(int argc, char* argv[]) {
    std::stringstream in("hello");
    zlib_stream::zip_istream zin(in);
    std::string line;
    std::getline(in, line);

    if (line == "hello")
    {
        return 0;
    }
    return 1;
}
