#include <embree3/rtcore.h>

int main() {
    RTCError error = rtcGetDeviceError(nullptr);
    return error == RTC_ERROR_NONE ? 0 : 1;
}
