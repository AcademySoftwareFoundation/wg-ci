#include <cstdlib>
#include <cstring>
#include <functional>
#include <iostream>
#include <memory>

#include <rpc/xdr.h>

template <typename T>
using deleter_unique_ptr = std::unique_ptr<T, std::function<void(T*)>>;

void close_file(FILE* const file)
{
    if (file)
        fclose(file);
}

void destroy_xdrs(XDR* const xdrs)
{
    if (xdrs)
        xdr_destroy(xdrs);
}

int main()
{
    const char* const tmp_path = std::getenv("TEST_PACKAGE_TEMP_PATH");
    if (!tmp_path)
    {
        std::cerr << "TEST_PACKAGE_TEMP_PATH environment variable not provided." << std::endl;
        return 1;
    }

    // Write something to file.
    {
        deleter_unique_ptr<FILE> file_ptr(fopen(tmp_path, "wb"), close_file);
        if (!file_ptr)
        {
            std::cerr << "Unable to open file \"" << tmp_path << "\" for writing." << std::endl;
            return 1;
        }

        XDR xdrs{};
        xdrstdio_create(&xdrs, file_ptr.get(), XDR_ENCODE);
        deleter_unique_ptr<XDR> xdrs_ptr(&xdrs, destroy_xdrs);

        const double value = 42.0;
        xdr_double(&xdrs, const_cast<double*>(&value));

        const char text[] = "Foundry";
        xdr_opaque(&xdrs, const_cast<char*>(text), sizeof(text));
    }

    // Read that something from file.
    {
        deleter_unique_ptr<FILE> file_ptr(fopen(tmp_path, "rb"), close_file);
        if (!file_ptr)
        {
            std::cerr << "Unable to open file \"" << tmp_path << "\" for reading." << std::endl;
            return 1;
        }

        XDR xdrs{};
        xdrstdio_create(&xdrs, file_ptr.get(), XDR_DECODE);
        deleter_unique_ptr<XDR> xdrs_ptr(&xdrs, destroy_xdrs);

        double value = 0.0;
        xdr_double(&xdrs, &value);
        if (value != 42.0)
        {
            std::cerr << "Expected " << 42.0 << "; encountered " << value << "." << std::endl;
            return 1;
        }

        char text[sizeof("Foundry")];
        memset(text, 0, sizeof(text));
        xdr_opaque(&xdrs, text, sizeof(text));
        if (std::string(text) != "Foundry")
        {
            std::cerr << "Expected \""
                      << "Foundry"
                      << "\"; encountered \"" << text << "\"." << std::endl;
            return 1;
        }
    }

    return 0;
}
