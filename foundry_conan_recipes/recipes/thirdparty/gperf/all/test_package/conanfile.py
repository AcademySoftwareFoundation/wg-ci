# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Foundry Visionmongers Ltd

import os
import subprocess

from conans import ConanFile
from conans.errors import ConanException


class GperfTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        binary = os.path.join(self.deps_cpp_info["gperf"].bin_paths[0], self.deps_user_info["gperf"].gperfexe)
        self.output.info("Checking for existence of '{}'".format(binary))
        if not os.path.isfile(binary):
            raise ConanException("'{}' does not exist".format(binary))
        try:
            self.output.info(subprocess.check_output([binary, "--version"]).decode("utf-8"))
        except subprocess.CalledProcessError as exc:
            raise ConanException(exc)
