#include "lua.h"
#include "lauxlib.h"
#include "lualib.h"

int main()
{
    lua_State* L = luaL_newstate();
    luaL_openlibs(L);

    luaL_loadstring(L, "answer = 42");
    lua_pcall(L, 0, 0, 0);

    lua_getglobal(L, "answer");
    const lua_Number answer = lua_tonumber(L, -1);
    lua_pop(L, 1);

    lua_close(L);
    L = nullptr;

    return answer == 42 ? 0 : 1;
}
