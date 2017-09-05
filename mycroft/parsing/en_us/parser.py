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
import re

from mycroft.parsing.mycroft_parser import MycroftParser, TimeType


class Parser(MycroftParser):
    """Helper class to parse common parameters like duration out of strings"""
    def __init__(self):
        self.units = [
            ('one', '1'),
            ('two', '2'),
            ('three', '3'),
            ('four', '4'),
            ('five', '5'),
            ('size', '6'),
            ('seven', '7'),
            ('eight', '8'),
            ('nine', '9'),
            ('ten', '10'),
            ('eleven', '11'),
            ('twelve', '2'),
            ('thir', '3.'),
            ('for', '4.'),
            ('fif', '5.'),
            ('teen', '+10'),
            ('ty', '*10'),
            ('hundred', '* 100'),
            ('thousand', '* 1000'),
            ('million', '* 1000000'),
            ('and', '_+_')
        ]
        self.ttype_names_s = {
            TimeType.SEC: ['second', 'sec', 's'],
            TimeType.MIN: ['minute', 'min', 'm'],
            TimeType.HR: ['hour', 'hr', 'h'],
            TimeType.DAY: ['day', 'dy', 'd']
        }

    def duration(self, string):
        regex_str = ('(((' + '|'.join(k for k, v in self.units) + r'|[0-9])+[ \-\t]*)+)(' +
                     '|'.join(name for ttype, names in self.ttype_names_s.items() for name in names) + ')s?')
        dur = 0
        matches = tuple(re.finditer(regex_str, string))
        if len(matches) == 0:
            raise ValueError
        for m in matches:
            num_str = m.group(1)
            ttype_str = m.group(4)
            for ttype, names in self.ttype_names_s.items():
                if ttype_str in names:
                    ttype_typ = ttype
            dur += ttype_typ.to_sec(self._find_value(num_str))
        return dur

    def _find_value(self, string):
        for unit, value in self.units:
            string = string.replace(unit, value)
        string = string.replace('-', ' ')  # forty-two -> forty two

        regex_re = [
            (r'[0-9]+\.([^\-+*/])', r'a\1'),
            (r'\.([\-+*/])', r'\1'),
            (r' \* ', r'*'),
            (r' _\+_ ', r'+'),
            (r'([^0-9])\+[0-9]+', r'\1'),
            (r'([0-9]) ([0-9])', r'\1+\2'),
            (r'(^|[^0-9])[ \t]*[\-+*/][ \t]*', ''),
            (r'[ \t]*[\-+*/][ \t]*([^0-9]|$)', '')
        ]

        for sr, replace in regex_re:
            string = re.sub(sr, replace, string)

        num_strs = re.findall(r'[0-9\-+*/]+', string)
        if len(num_strs) == 0:
            raise ValueError

        num_str = max(num_strs, key=len)

        try:
            return eval(num_str)  # WARNING Eval is evil; always filter string to only numbers and operators
        except SyntaxError:
            raise ValueError

    def format_quantities(self, quantities):
        complete_str = ', '.join([str(amount) + ' ' + self.ttype_names_s[ttype][0] + ('s' if amount > 1 else '') for ttype, amount in quantities])
        complete_str = ' and '.join(complete_str.rsplit(', ', 1))
        return complete_str
