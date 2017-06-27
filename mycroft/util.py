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
import logging
import inspect


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


def init_logging():
    level = logging.DEBUG  # logging.getLevelName(config.get('log_level', 'DEBUG'))
    fmt = '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s'
    datefmt = '%H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt)
    handler = logging.FileHandler('/var/tmp/mycroft.log')  # config.get('log_file'))
    handler.setFormatter(formatter)
    logging.basicConfig(handlers=[handler], level=level, format=fmt, datefmt=datefmt)


def get_logger(name=None):
    """
    Get a python logger with the name of the caller's module
    :return: a logger instance
    :rtype: logging.Logger
    """
    if name is None:
        try:
            name = inspect.getmodule(inspect.stack()[1][0]).__name__
        except IndexError:
            name = 'mycroft'

    return logging.getLogger(name)

