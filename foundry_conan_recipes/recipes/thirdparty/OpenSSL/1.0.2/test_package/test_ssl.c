#include "openssl/ssl.h"

int main(void) {

    SSL_library_init();
    /* will leak */

    return 0;
}
