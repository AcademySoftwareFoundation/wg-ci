#include "sentry.h"

// from https://docs.sentry.io/platforms/native/#configure

int main()
{
    sentry_options_t *options = sentry_options_new();
    sentry_options_set_dsn(options, "https://examplePublicKey@o0.ingest.sentry.io/0");
    sentry_options_set_release(options, "my-project-name@2.3.12");
    sentry_init(options);

    sentry_close();
}
