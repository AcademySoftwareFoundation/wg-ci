#include <log4cplus/configurator.h>
#include <log4cplus/logger.h>
#include <log4cplus/loggingmacros.h>

int main()
{
    log4cplus::BasicConfigurator config;
    config.configure();

    log4cplus::Logger logger =
        log4cplus::Logger::getInstance(LOG4CPLUS_TEXT("main"));

    LOG4CPLUS_INFO(logger, LOG4CPLUS_TEXT("log4cplus Test Complete."));
    return 0;
}
