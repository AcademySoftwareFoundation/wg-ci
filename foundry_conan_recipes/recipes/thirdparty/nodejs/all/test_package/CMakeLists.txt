cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_program(
    NODEJS_NODE_EXE
    NAMES
        "node"
    REQUIRED
)
message(STATUS "Found NodeJS executable at '${NODEJS_NODE_EXE}'")

enable_testing()
add_test(
    NAME nodejs_version_test
    COMMAND ${NODEJS_NODE_EXE} -e "console.log('Hello from Node.js', process.version)"
)
