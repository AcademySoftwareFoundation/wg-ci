#include <OpenVR/openvr.h>
#include <string>

int main() {
    std::string const expected = "VRInitError_None";
    std::string output = vr::VR_GetVRInitErrorAsSymbol(vr::VRInitError_None);

    return expected == output ? 0 : 1;
}
