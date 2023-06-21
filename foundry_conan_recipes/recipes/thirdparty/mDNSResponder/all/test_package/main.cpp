#include <mDNSResponder/dns_sd.h>

int main() {
    DNSServiceRef SharedRef;
    DNSServiceCreateConnection(&SharedRef);
    DNSServiceRefDeallocate(SharedRef);

    return 0;
}
