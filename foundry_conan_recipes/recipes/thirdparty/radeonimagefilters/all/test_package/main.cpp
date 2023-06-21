#include <RadeonImageFilters.h>

int main()
{
    const char* result = rifGetErrorCodeDescription(RIF_SUCCESS);
    return result ? 0 : 1;
}
