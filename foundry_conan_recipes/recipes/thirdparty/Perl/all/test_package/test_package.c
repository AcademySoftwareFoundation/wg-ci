/* derive from https://perldoc.perl.org/perlembed.html */

#include "EXTERN.h"
#include "perl.h"

int main(int argc, char **argv, char **env) {

    PERL_SYS_INIT3(&argc,&argv,&env);
    PerlInterpreter *my_perl = perl_alloc();
    perl_construct(my_perl);
    perl_destruct(my_perl);
    perl_free(my_perl);
    PERL_SYS_TERM();

    return 0;
}
