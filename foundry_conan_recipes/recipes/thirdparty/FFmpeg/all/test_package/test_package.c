#include <libavformat/avformat.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
#if LIBAVFORMAT_VERSION_MAJOR < 5    
    av_register_all();
#endif    
    printf("av_format version: %d.%d.%d",
        LIBAVFORMAT_VERSION_MAJOR,
        LIBAVFORMAT_VERSION_MINOR,
        LIBAVFORMAT_VERSION_MICRO
    );
    return 0;
}