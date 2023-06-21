#include <jemalloc/jemalloc.h>

int main()
{
    const size_t size = 1024 * 1024;
    void* buffer = je_malloc(size);
    if (!buffer)
        return 1;

    for (size_t i = 0; i < size; ++i)
    {
        static_cast<char*>(buffer)[i] = 'a';
    }

    je_free(buffer);
    buffer = nullptr;

    return 0;
}
