#
# Copyright (c) 2017 Mycroft AI, Inc.
#
# This file is part of Mycroft Simple
# (see https://github.com/MatthewScholefield/mycroft-simple).
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
#
from time import sleep

from threading import Thread, Event

from mycroft.formats.dialog_format import DialogFormat
from mycroft.formats.faceplate_format import FaceplateFormat
from mycroft.util import logger


class FormatManager:
    """Holds all formats and provides an interface to access them"""

    def __init__(self, path_manager):
        self.formats = []

        def create(cls, prefix):
            instance = None
            try:
                instance = cls(path_manager)
                self.formats.append(instance)
            except Exception as e:
                logger.print_e(e, self.__class__.__name__)
            self._reuse_methods(cls, instance, prefix)
            return instance

        create(DialogFormat, 'dialog_')
        create(FaceplateFormat, 'faceplate_')
        self.reset_event = Event()
        self.reset_event.set()

    def _reuse_methods(self, cls, obj, prefix):
        def create_wrapper(func):
            def wrapper(*args, **kwargs):
                if obj is not None:
                    return func(obj, *args, **kwargs)
                else:
                    return ''
            return wrapper

        funcs = [
            a for a in dir(cls)
            if not a.startswith('_') and callable(getattr(cls, a))
        ]
        for func in funcs:
            print('Setting attribute ' +  prefix + func)
            setattr(self, prefix + func, create_wrapper(getattr(cls, func)))

    def generate(self, name, results):
        for i in self.formats:
            i.generate(name, results)

    def set_reset_event(self, event):
        self.reset_event = event
        Thread(target=self.wait_for_reset, daemon=True).start()

    def _reset(self):
        for i in self.formats:
            i._reset()

    def wait_for_reset(self):
        self.reset_event.wait()
        self._reset()

    def reset(self):
        if self.reset_event.is_set():
            self._reset()
