// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <iostream>

#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

#ifndef RAPIDJSON_HAS_STDSTRING
#error "RapidJson is missing std::string support."
#endif


int main()
{
    const char* const json = "{ \"str_value\": \"hello\", \"int_value\": 42 }";

    rapidjson::Document d;
    d.Parse(json);

    d["int_value"].SetInt(137);

    rapidjson::Value float_value(-17.4f);
    d.AddMember("float_value", float_value, d.GetAllocator());

    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    d.Accept(writer);

    std::cout << buffer.GetString() << std::endl;
    return 0;
}
