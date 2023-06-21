// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>
#include <zmq.h>

int main ()
{
    int errorCode = EMTHREAD;
    const char* errorString = zmq_strerror(errorCode);

    if (errorString == NULL) {
    	std::cout << "Failed to retreive error string for error code " << errorCode << '\n';
    	return 1;
    }
    std::cout << "Retrieved error message for error code: \"" << errorString << "\".\n";
    std::cout << "Success\n";
    return 0;
}

