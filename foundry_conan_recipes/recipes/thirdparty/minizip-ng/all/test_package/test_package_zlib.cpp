#include <iostream>

#include "mz_strm_zlib.h"

int main(void)
{
    // For example OpenColorIO requires a minizip-ng library that supports zlib. The test package
    // is added to verify that it can be linked against it.

    void* stream = NULL;

    mz_stream_zlib_create(&stream);

    if (stream == NULL)
    {
        std::cerr << "ERROR: Unable to create zlib stream." << std::endl;
        return 1;
    }

    mz_stream_zlib_delete(&stream);

    return 0;
}
