#include "imgui.h"

int main()
{
    const char* const version = ImGui::GetVersion();
    if (!version)
        return 1;
    return strlen(version) > 0 ? 0 : 1;
}
