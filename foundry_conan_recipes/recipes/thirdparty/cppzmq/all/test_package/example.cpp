#include <future>
#include <string>
#include <thread>

#include <iostream>

#include "zmq.hpp"
#include "zmq_addon.hpp"

static bool g_received = false;
static bool g_validated = false;

static const char kChannel[] = "inproc://#1";
static const char kEnvelope[] = "A";
static const char kMessage[] = "Hello World!";

void PublisherThread(zmq::context_t* const ctx)
{
    zmq::socket_t publisher(*ctx, zmq::socket_type::pub);
    publisher.bind(kChannel);

    while (!g_received)
    {
        publisher.send(zmq::str_buffer(kEnvelope), zmq::send_flags::sndmore);
        publisher.send(zmq::str_buffer(kMessage));
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

void SubscriberThread(zmq::context_t* const ctx)
{
    zmq::socket_t subscriber(*ctx, zmq::socket_type::sub);
    subscriber.connect(kChannel);
    subscriber.set(zmq::sockopt::subscribe, kEnvelope);

    while (!g_received)
    {
        std::vector<zmq::message_t> recv_msgs;
        const zmq::recv_result_t result =
            zmq::recv_multipart(subscriber, std::back_inserter(recv_msgs));

        g_received = true;

        if (!result)
        {
            std::cerr << "Failed to receive data" << std::endl;
            break;
        }

        const std::string message{recv_msgs[1].to_string()};
        if (message != kMessage)
        {
            std::cerr << "Data mismatch:" << kMessage << " != " << message
                      << std::endl;
            break;
        }

        g_validated = true;
    }
}

int main()
{
    zmq::context_t ctx(0);

    auto publisherThread =
        std::async(std::launch::async, PublisherThread, &ctx);
    auto subscriberThread =
        std::async(std::launch::async, SubscriberThread, &ctx);

    publisherThread.wait();
    subscriberThread.wait();

    return g_validated ? 0 : 1;
}
