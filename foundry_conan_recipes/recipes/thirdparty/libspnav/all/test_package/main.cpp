#include <spnav.h>

int main() {

    // Is ok for it to fail, as you might not actually have any drivers installed
    spnav_open();
    spnav_close();

    return 0;
}
