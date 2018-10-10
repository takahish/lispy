# Copyright 2018 Takahiro Ishikawa. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import unittest
from clispy.symbol import *
from clispy import utility


class UnitTestCase(unittest.TestCase):
    def test_to_string(self):
        self.assertEqual(utility.to_string(True), 'T')
        self.assertEqual(utility.to_string(False), 'NIL')
        self.assertEqual(utility.to_string(Symbol('x')), 'x')
        self.assertEqual(utility.to_string("string"), '"string"')
        self.assertEqual(utility.to_string([1, 2, 3]), '(1 2 3)')
        self.assertEqual(utility.to_string(2 + 3j), '(2+3i)')
        self.assertEqual(utility.to_string(1), '1')

    def test_require(self):
        x = []
        self.assertRaisesRegex(SyntaxError, "() wrong length", utility.require, x, x != [])

    def test_callcc(self):
        self.assertEqual(utility.callcc(lambda throw: 5 + 10 * throw(1)), 1)
        self.assertEqual(utility.callcc(lambda throw: 5 + 10 * 1), 15)
        self.assertEqual(utility.callcc(lambda throw: 5 + 10 * utility.callcc(lambda escape: 100 * escape(3))), 35)
        self.assertEqual(utility.callcc(lambda throw: 5 + 10 * utility.callcc(lambda escape: 100 * throw(3))), 3)
        self.assertEqual(utility.callcc(lambda throw: 5 + 10 * utility.callcc(lambda escape: 100 * 1)), 1005)