#
# Copyright (c) 2022 The Foundry Visionmongers Ltd. All Rights Reserved.
#

cmake_minimum_required(VERSION 3.0.0)
project(TestPackage)

find_package(bulletphysics CONFIG REQUIRED)

add_executable(BulletPhysicsTest main.cpp)

target_link_libraries(BulletPhysicsTest PRIVATE Bullet::Bullet)

enable_testing()

add_test(
    NAME
        bullet_physics_basic_test
    WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}
    COMMAND
        BulletPhysicsTest
)
