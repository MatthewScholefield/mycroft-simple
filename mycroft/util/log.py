#
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
#
import sys
import inspect
import logging
from traceback import format_exception


def _make_log_method(fn):
    @classmethod
    def method(cls, *args, **kwargs):
        cls._log(fn, *args, **kwargs)

    method.__func__.__doc__ = fn.__doc__
    return method


class LOG:
    """
    Custom logger class that acts like logging.Logger
    The logger name is automatically generated by the module of the caller

    Usage:
        logger.debug('My message: %s', debug_str)
        logger('custom_name').debug('Another message')
    """
    _custom_name = None

    # Copy actual logging methods from logging.Logger
    # Usage: LOG.debug(message)
    debug = _make_log_method(logging.Logger.debug)
    info = _make_log_method(logging.Logger.info)
    warning = _make_log_method(logging.Logger.warning)
    error = _make_log_method(logging.Logger.error)
    exception = _make_log_method(logging.Logger.exception)

    @classmethod
    def init(cls, config):
        cls.level = logging.getLevelName(config.get('log_level', 'DEBUG'))

        fmt = '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s'
        datefmt = '%H:%M:%S'
        formatter = logging.Formatter(fmt, datefmt)
        cls.fh = logging.FileHandler(config['log_file'], mode='w')
        cls.fh.setFormatter(formatter)
        cls.create_logger('')  # Enables logging in external modules

        def make_method(fn):
            return lambda *args, **kwargs: cls._log(fn, *args, **kwargs)

    @classmethod
    def create_logger(cls, name):
        l = logging.getLogger(name)
        l.propagate = False
        if not hasattr(cls, 'fh') or not hasattr(cls, 'level'):
            return l

        l.addHandler(cls.fh)
        l.setLevel(cls.level)
        return l

    def __init__(self, name):
        LOG._custom_name = name

    @classmethod
    def _log(cls, func, *args, **kwargs):
        if LOG._custom_name is not None:
            name = LOG._custom_name
            LOG._custom_name = None
        else:
            # Stack:
            # [0] - _log()
            # [1] - debug(), info(), warning(), or error()
            # [2] - caller
            stack = inspect.stack()

            # Record:
            # [0] - frame object
            # [1] - filename
            # [2] - line number
            # [3] - function
            # ...
            record = stack[2]
            mod = inspect.getmodule(record[0])
            mod_name = mod.__name__ if mod else ''
            name = mod_name + ':' + record[3] + ':' + str(record[2])
        func(cls.create_logger(name), *args, **kwargs)

    @classmethod
    def print_trace(cls, location='', warn=False, *args, **kwargs):
        trace_lines = format_exception(*sys.exc_info())
        if warn:
            intro = 'Warning' + ('in ' + location + ': ' if location else ': ')
            trace_str = intro + trace_lines[-1].strip()
            f = logging.Logger.info
        else:
            trace_str = '\n' + ''.join(trace_lines)
            if location:
                trace_str = '\n=== ' + location + ' ===' + trace_str
            trace_str = '\n' + trace_str
            f = logging.Logger.error
        cls._log(f, trace_str, *args, **kwargs)