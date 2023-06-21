// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#undef NDEBUG  // Always enable assertions.
#include <cassert>
#include <iostream>

#include <tinyxml/tinyxml.h>

#ifndef TIXML_USE_STL
#error "TinyXML package does not provide STL support!"
#endif


// Copied from the TinyXML tutorial at
// http://www.grinninglizard.com/tinyxmldocs/tutorial0.html.
static const char* const g_testXML = R"XML(
<?xml version="1.0" ?>
<MyApp>
    <!-- Settings for MyApp -->
    <Messages>
        <Welcome>Welcome to MyApp</Welcome>
        <Farewell>Thank you for using MyApp</Farewell>
    </Messages>
    <Windows>
        <Window name="MainFrame" x="5" y="15" w="400" h="250" />
    </Windows>
    <Connection ip="192.168.0.1" timeout="123.456000" />
</MyApp>
)XML";

int main()
{
    TiXmlDocument doc;
    doc.Parse(g_testXML);
    assert(!doc.Error());

    TiXmlElement* root = doc.RootElement();
    assert(strcmp(doc.RootElement()->Value(), "MyApp") == 0);
    assert(root->ValueStr() == "MyApp");

    TiXmlElement* window = root->FirstChildElement("Windows")->FirstChildElement("Window");
    assert(window != nullptr);

    std::string name;
    assert(window->QueryStringAttribute("name", &name) == TIXML_SUCCESS);
    assert(name == "MainFrame");

    int w;
    assert(window->QueryIntAttribute("w", &w) == TIXML_SUCCESS);
    assert(w == 400);

    return 0;
}
