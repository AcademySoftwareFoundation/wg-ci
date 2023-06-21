#include <avahi-client/client.h>
#include <avahi-client/lookup.h>

#include <avahi-common/malloc.h>
#include <avahi-common/error.h>

#include <avahi-qt/qt-watch.h>

#include <iostream>

static void qt_client_callback(AvahiClient* c, AvahiClientState state, void* userdata)
{
    if (state == AVAHI_CLIENT_FAILURE)
    {
        std::cerr << "Server connection failure: " << avahi_strerror(avahi_client_errno(c)) << std::endl;
    }
}

bool test_qt5_poll()
{
    const AvahiPoll* qt5_poll = avahi_qt_poll_get();
    if (!qt5_poll)
    {
        std::cerr << "Failed to create simple poll object." << std::endl;
        return false;
    }

    int error = 0;
    AvahiClient* client = avahi_client_new(qt5_poll, static_cast<AvahiClientFlags>(0), qt_client_callback, nullptr, &error);
    if (!client)
    {
        std::cerr << "Failed to create client: " << avahi_strerror(error) << std::endl;
        return false;
    }

    if (client)
    {
        avahi_client_free(client);
    }

    return true;
}

int main()
{
    if (!test_qt5_poll())
    {
        return -1;
    }

    return 0;
}
