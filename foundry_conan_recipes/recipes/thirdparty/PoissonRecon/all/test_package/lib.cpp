#include "lib.h"

#include "MultiGridOctest.h"


void PoissonTest()
{
    using namespace Foundry::PoissonMeshing;

    ParamStruct params;
    Mesh mesh;
    Vertex vertices[3] = {
        {0.0f,0.0f,0.0f},
        {1.0f,0.0f,0.0f},
        {1.0f,1.0f,0.0f}
    };
    Face face = {0, 1, 2};

    mesh.allocateVertices(3);
    mesh.allocateFaces(1);
    mesh._faces[0] = face;
    mesh._vertices[0] = vertices[0];
    mesh._vertices[1] = vertices[1];
    mesh._vertices[2] = vertices[2];

    float normals[1][3] = { { 0.0f, 0.0f, 1.0f} };
    params.setDataPtr(&normals[0][0], 3*1);
    mainFuncFromParsedArgs(params, mesh);
}
