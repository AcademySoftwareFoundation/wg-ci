#undef NDEBUG  // Always enable assertions.
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_RESIZE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include <stb/stb_image.h>
#include <stb/stb_image_resize.h>
#include <stb/stb_image_write.h>


int main()
{
    // Create a texture in memory.
    int originalDim[] = { 154, 96 };
    int originalNumChannels = 4;
    size_t originalNumBytes = originalNumChannels * originalDim[0] * originalDim[1];

    uint8_t *originalTexels = malloc(originalNumBytes);
    for (int y = 0; y < originalDim[1]; ++y) {
        for (int x = 0; x < originalDim[0]; ++x) {
            uint8_t *t = originalTexels + 4*(x + y*originalDim[0]);
            t[0] = (uint8_t)(255.0f*x / originalDim[0]);
            t[1] = (uint8_t)(255.0f*y / originalDim[1]);
            t[2] = 0x00;
            t[3] = 0xFF;
        }
    }

    // Write the texture to disk using stb_image_write.
    const char *const path = "test_texture.png";
    int originalStride = originalNumChannels * originalDim[0];
    int writeResult = stbi_write_png(path, originalDim[0], originalDim[1], originalNumChannels, originalTexels, originalStride);
    assert(writeResult != 0);

    // Read the texture back in using stb_image.
    int loadedDim[] = { 0, 0 };
    int loadedNumChannels = 0;
    uint8_t *loadedTexels = stbi_load(path, &loadedDim[0], &loadedDim[1], &loadedNumChannels, originalNumChannels);
    assert(loadedTexels != NULL);
    assert(loadedDim[0] == originalDim[0]);
    assert(loadedDim[1] == originalDim[1]);
    assert(loadedNumChannels == originalNumChannels);

    stbi_image_free(loadedTexels);

    // Resize the texture using stb_image_resize.
    int resizedDim[2] = { 3*originalDim[0]/2, 7*originalDim[1]/4 };
    size_t numResizedBytes = originalNumChannels * resizedDim[0] * resizedDim[1];
    uint8_t *resizedTexels = malloc(numResizedBytes);

    int resizeResult = stbir_resize_uint8(originalTexels, loadedDim[0], loadedDim[1], 0,
                                          resizedTexels, resizedDim[0], resizedDim[1], 0,
                                          originalNumChannels);
    assert(resizeResult != 0);

    free(resizedTexels);
    free(originalTexels);
    
    return 0;
}
