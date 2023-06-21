#include "openssl/ssl.h"

int main(void) {

    OPENSSL_init();
    /* will leak */

    return 0;
}
