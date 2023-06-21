# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

from conan import ConanFile

from os import path

class TestQMake(ConanFile):
    settings = ['os', 'arch']

    def test(self):
        self.run('echo $PWD')
        self.run(f'qmake -o Makefile {path.dirname(__file__)}/hello.pro')
        if self.settings.os == 'Windows':
            self.run('nmake')
        else:
            self.run('make')
