#include <stdint.h>
#include <stdio.h>

#include "lauxlib.h"
#include "lua.h"
#include "lualib.h"

int main(const int argc, const char* const argv[])
{
    if (argc < 2)
    {
        printf("[C]: Invalid arguments. Provide path to Lua file.\n");
        return 1;
    }

    lua_State* L = luaL_newstate();
    if (!L)
    {
        printf("[C]: Failed to create Lua state.\n");
        return 1;
    }

    luaL_openlibs(L);

    int r = luaL_loadfile(L, argv[1]);
    if (r != LUA_OK)
    {
        const char* msg = lua_tostring(L, -1);
        printf("[C]: Failed to load Lua file: %s\n", msg);
        return 1;
    }

    if (lua_pcall(L, 0, 0, 0) != LUA_OK)
    {
        const char* msg = lua_tostring(L, -1);
        printf("[Lua]: Unexpected error: %s\n", msg);
        return 1;
    }

    lua_close(L);

    return 0;
}
