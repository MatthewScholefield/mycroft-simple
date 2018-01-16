#!/usr/bin/env python3
# Copyright (c) 2017 Mycroft AI, Inc.
#
# This file is part of Mycroft Light
# (see https://github.com/MatthewScholefield/mycroft-light).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import sys

sys.path += ['.']  # noqa

from time import sleep
from mycroft.util import log
from mycroft.root import Root


def info(message):
    print(message)
    log.info(message)


def main():
    rt = Root()

    if rt.config['use_server']:
        rt.config.load_remote()

    rt.intent.all.compile()
    rt.frontends.all.run(gp_daemon=True)

    try:
        rt.main_thread.wait()
    except KeyboardInterrupt:
        pass
    log.info('Quiting...')
    sleep(0.1)
    print()


if __name__ == '__main__':
    main()