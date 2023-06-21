#include "tiffio.h"
#include <stdio.h>
int main()
{
    TIFF* tif = TIFFOpen("foo.tif", "w");
    if (tif != NULL)
    {
        uint64_t scanlinesize = TIFFScanlineSize64(tif);
        printf("Scan line size is %llu\n", scanlinesize);
        TIFFClose(tif);
    }
    return 0;
}
