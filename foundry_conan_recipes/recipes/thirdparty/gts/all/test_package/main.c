#include <stdio.h>

#include "gts.h"

int main()
{
    GtsSurface* surface = gts_surface_new(
        gts_surface_class(), gts_face_class(), gts_edge_class(), gts_vertex_class());

    if (!surface)
    {
        printf("ERROR: Unable to create surface.\n");
        return 1;
    }

    gts_object_destroy((GtsObject*)surface);

    return 0;
}
