#include <stdio.h>

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_GLYPH_H

#if !defined(FREETYPE_MAJOR) || !defined(FREETYPE_MINOR) || !defined(FREETYPE_PATCH)
#   error "FreeTrype version not defined."
#endif

int main(int argc, char **argv) {
    FT_Library library;
    
    // Initialise Freetype.
    int error = FT_Init_FreeType(&library);
    if (error) {
        fprintf(stderr, "Failed to initialize FreeType.\n");
        return 1;
    }

    // Attempt to load the test font.
    FT_Face face;
    error = FT_New_Face(library, EXAMPLE_FONT_FILE, 0, &face);
    if (error) {
        fprintf(stderr, "Failed to load test font.\n");
        return 2;
    } else {
        printf("Loaded test font:\n");
        if (face->num_glyphs<=0) {
            return 3;
        }
        for (size_t i = 0; i < face->num_fixed_sizes; ++i) {
            FT_Bitmap_Size* size = face->available_sizes + i;
            if (size->width<=0 || size->height<=0) {
                return 4;
            }
        }
        fflush(stdout);
    }
    // Shutdown Freetype.
    error = FT_Done_FreeType(library);
    if (error) {
        fprintf(stderr, "Failed to shutdown FreeType.\n");
        return 5;
    }
    return 0;
}
