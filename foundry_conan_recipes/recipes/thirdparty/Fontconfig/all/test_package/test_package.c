#include <fontconfig/fontconfig.h>
#include <stddef.h>
#include <stdio.h>

int main(int argc, const char** argv) {
    FcConfig *config;
    const FcChar8 *name = NULL;
    FcChar8 *filename;
    int ret=FcInit();
    if (ret!=FcTrue) {
        return -1;
    }

    config = FcConfigCreate();
    if (NULL==config) {
        return -2;
    }

    /* this will return NULL if the embedded path in the library does not exist on client machines */
    filename = FcConfigGetFilename(config, name);
    if (NULL==filename) {
        return -3;
    }

    printf("Fontconfig configuration filename is '%s'", filename);

    FcConfigDestroy(config);

    FcFini();
    return 0;
}
