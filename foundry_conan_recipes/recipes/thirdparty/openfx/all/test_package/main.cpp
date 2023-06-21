// This file is to assert that the headers can be located and that a program can be built.

#include "ofxCore.h"
#include "ofxImageEffect.h"
#include "ofxInteract.h"
#include "ofxKeySyms.h"
#include "ofxMemory.h"
#include "ofxMessage.h"
#include "ofxMultiThread.h"
#include "ofxParam.h"
#include "ofxParametricParam.h"
#include "ofxPixels.h"
#include "ofxProgress.h"
#include "ofxProperty.h"
#include "ofxTimeLine.h"

int main()
{
    OfxPlugin plugin{};
    plugin.pluginApi = "My API";
    plugin.apiVersion = 1;
    plugin.pluginIdentifier = "My ID";
    plugin.pluginVersionMajor = 42;
    plugin.pluginVersionMinor = 0;
    plugin.setHost = nullptr;
    plugin.mainEntry = nullptr;

    OfxMultiThreadSuiteV1 mtsuite{};

    return 0;
}
