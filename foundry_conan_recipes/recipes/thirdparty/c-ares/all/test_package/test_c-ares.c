#include "ares.h"
#include <stdio.h>

int main()
{
    int res;
    ares_channel channel;

    if ((res = ares_library_init(ARES_LIB_INIT_ALL)) != ARES_SUCCESS)
    {
        printf("ares failed: %d: '%s'\n", res, ares_strerror(res));
        return 1;
    }

    if ((res = ares_init(&channel)) != ARES_SUCCESS)
    {
        printf("ares failed: %d: '%s'\n", res, ares_strerror(res));
        return 2;
    }

    ares_library_cleanup();

    return 0;
}
