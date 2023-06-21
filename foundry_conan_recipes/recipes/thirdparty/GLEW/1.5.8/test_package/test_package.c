#include <GL/glew.h>
#include <stddef.h>

int main ()
{
    const GLubyte* glew_version = glewGetString(GLEW_VERSION);
    if (NULL == glew_version)
    {
        return -1;
    }
    return 0;
}

