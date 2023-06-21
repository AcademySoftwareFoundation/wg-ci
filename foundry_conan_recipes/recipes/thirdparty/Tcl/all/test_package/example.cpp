#ifdef __APPLE__
#include "Tcl/tcl.h"
#else
#include "tcl.h"
#endif

int main() {
    Tcl_Interp *tcl = Tcl_CreateInterp();
    Tcl_DeleteInterp(tcl);
    return 0;
}
