#include <iostream>
#include <string>

#include <glib.h>

int main()
{
    GList* list{nullptr};

    list = g_list_append(list, static_cast<gpointer>(const_cast<char*>("Hello")));
    list = g_list_append(list, static_cast<gpointer>(const_cast<char*>("World")));

    if (g_list_length(list) != 2)
    {
        std::cerr << "Unexpected list length." << std::endl;
        return 1;
    }

    if (static_cast<const char*>(g_list_first(list)->data) != std::string("Hello"))
    {
        std::cerr << "Entry mismatch." << std::endl;
        return 1;
    }

    if (static_cast<const char*>(g_list_last(list)->data) != std::string("World"))
    {
        std::cerr << "Entry mismatch." << std::endl;
        return 1;
    }

    g_list_free(list);

    return 0;
}
