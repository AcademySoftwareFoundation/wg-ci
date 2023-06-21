// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include "FTGL/ftgl.h"

/**
 * Example from <a href="http://ftgl.sourceforge.net/docs/html/ftgl-tutorial.html"/>
 */
int main() {
    // Create a pixmap font from a TrueType file.
    FTGLPixmapFont font(EXAMPLE_FONT_FILE);

    // If something went wrong, bail out.
    if (font.Error()) {
        return -1;
    }
    // Set the face size and the character map. If something went wrong, bail out.
    font.FaceSize(72);

    // If something went wrong, bail out.
    if (font.Error()) {
        return -1;
    }

    if (font.Advance("fubar")==0.0f) {
        return -3;
    }
    return 0;
}
