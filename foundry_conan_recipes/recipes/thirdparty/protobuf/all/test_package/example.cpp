#include "example.pb.h"

int main()
{
    example::HelloWorld hello_world_message;
    hello_world_message.set_response("From Conan");

    return 0;
}
