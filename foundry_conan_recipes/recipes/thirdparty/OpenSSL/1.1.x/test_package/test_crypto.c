#include "openssl/ssl.h"

int main(void) {

    OPENSSL_init_crypto(OPENSSL_INIT_NO_ADD_ALL_CIPHERS | OPENSSL_INIT_NO_ADD_ALL_DIGESTS, NULL);
    /* will leak */

    return 0;
}
