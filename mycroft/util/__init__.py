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
import sys
import os
import inspect
import logging
from contextlib import contextmanager
from ctypes import *


def to_camel(snake):
    """time_skill -> TimeSkill"""
    return snake.title().replace('_', '')


def to_snake(camel):
    """TimeSkill -> time_skill"""
    return ''.join('_' + x if 'A' <= x <= 'Z' else x for x in camel).lower()[1:]


def split_sentences(text):
    """
    Turns a string of multiple sentences into a list of separate ones
    As a side effect, .?! at the end of a sentence are removed
    """
    sents = list(filter(None, text.split('. ')))

    # Rejoin sentences with an initial
    # ['Harry S', 'Truman'] -> ['Harry S. Truman']
    i = 0
    corrected_sents = []
    while i < len(sents):
        if sents[i][-2] == ' ' and i < len(sents) - 1:
            corrected_sents += [sents[i] + '. ' + sents[i + 1]]
            i += 2
        else:
            corrected_sents += [sents[i]]
            i += 1

    sents = corrected_sents

    for punc in ['?', '!']:
        new_sents = []
        for i in sents:
            new_sents += i.split(punc + ' ')
        sents = new_sents

    return sents


class logger:
    """
    Custom logger class that acts like logging.Logger
    The logger name is automatically generated by the module of the caller

    Usage:
        logger.debug('My message: %s', debug_str)
        logger('custom_name').debug('Another message')
    """

    _custom_name = None

    @staticmethod
    def init(config):
        level = logging.getLevelName(config.get('log_level', 'DEBUG'))
        fmt = '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s'
        datefmt = '%H:%M:%S'
        formatter = logging.Formatter(fmt, datefmt)
        handler = logging.FileHandler(config.get('log_file'), mode='w')
        handler.setFormatter(formatter)
        logging.basicConfig(handlers=[handler], level=level, format=fmt, datefmt=datefmt)

    def __init__(self, name):
        logger._custom_name = name

    @staticmethod
    def _log(func, msg, args):
        if logger._custom_name is not None:
            name = logger._custom_name
            logger._custom_name = None
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
            name = inspect.getmodule(record[0]).__name__ + ':' + record[3] + ':' + str(record[2])
        func(logging.getLogger(name), msg, *args)

    @staticmethod
    def debug(msg, *args):
        logger._log(logging.Logger.debug, msg, args)

    @staticmethod
    def info(msg, *args):
        logger._log(logging.Logger.info, msg, args)

    @staticmethod
    def warning(msg, *args):
        logger._log(logging.Logger.warning, msg, args)

    @staticmethod
    def error(msg, *args):
        logger._log(logging.Logger.error, msg, args)

    @staticmethod
    def print_e(e, location=''):

        typ, obj, tb = sys.exc_info()[:3]
        line = tb.tb_lineno
        file = os.path.split(tb.tb_frame.f_code.co_filename)[1]
        file_line = file + ':' + str(line)
        if location != '':
            location += ', '

        intro = 'Exception in ' + location + file_line + ', '
        logger._log(logging.Logger.warning, intro + typ.__name__ + ': ' + str(e), ())


@contextmanager
def redirect_alsa_errors():
    """
    Redirects ALSA errors to logger rather than stdout
    Usage:
        with redirect_alsa_errors():
            do_something_that_generates_alsa_errors()
    """
    func_type = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

    def alsa_err_handler(filename, line, function, err, fmt):
        logger('alsa').debug(filename.decode() + ':' + function.decode() + ', ' + fmt.decode())

    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(func_type(alsa_err_handler))
    yield
    asound.snd_lib_error_set_handler(None)
