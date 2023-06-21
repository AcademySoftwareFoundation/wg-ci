#include "unicode/ucol.h"
#include <iostream>

int main()
{
    UErrorCode err = U_ZERO_ERROR;

    UCollator *collator = ucol_open("da_DK", &err);

    if (U_FAILURE(err))
    {
        std::cerr << "Error open collator: " << err << std::endl;
        return 1;
    }

    ucol_close(collator);
    return 0;
}
