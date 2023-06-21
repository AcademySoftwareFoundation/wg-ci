#include "openssl/ssl.h"

int main(void) {

    OPENSSL_init_ssl(OPENSSL_INIT_NO_LOAD_SSL_STRINGS, NULL);
    /* will leak */

    return 0;
}
