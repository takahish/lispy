from unittest import TestCase
import io
from clispy.symbol import _Symbol
from clispy.symbol import _quote, _if, _set, _define, _lambda, _begin, _define_macro
from clispy.parser import _eof_object, _InPort, _atom, _read_ahead, _read, _parse
from clispy.parser import _readchar, _to_string, _require, _expand

class UnitTestCase(TestCase):
    def test_eof_object(self):
        self.assertIsInstance(_eof_object, _Symbol)

    def testInPort(self):
        inport = _InPort(io.StringIO('(list 2 3 "string")'))

        self.assertIsInstance(inport, _InPort)

        # tokens
        self.assertEqual(inport.next_token(), '(')
        self.assertEqual(inport.next_token(), 'list')
        self.assertEqual(inport.next_token(), '2')
        self.assertEqual(inport.next_token(), '3')
        self.assertEqual(inport.next_token(), '"string"')
        self.assertEqual(inport.next_token(), ')')

        # #<eof-object>
        self.assertIsInstance(inport.next_token(), _Symbol)
        self.assertEqual(inport.next_token(), _eof_object)

    def test_atom(self):
        self.assertTrue(_atom('#t'))
        self.assertFalse(_atom('#f'))
        self.assertEqual(_atom('"string"'), 'string')

        self.assertIsInstance(_atom('2'), int)
        self.assertEqual(_atom('2'), 2)
        self.assertIsInstance(_atom('2.3'), float)
        self.assertEqual(_atom('2.3'), 2.3)
        self.assertIsInstance(_atom('2+3i'), complex)
        self.assertEqual(_atom('2+3i'), 2+3j)
        self.assertIsInstance(_atom('sym'), _Symbol)
        
    def test_read_ahead(self):
        # success to tokenize
        inport = _InPort(io.StringIO('(list 2 3 "string")'))
        token = inport.next_token()
        self.assertEqual(_read_ahead(token, inport), ['list', 2, 3, "string"])

        # quote
        inport = _InPort(io.StringIO("'(+ 2 3)"))
        token = inport.next_token()
        self.assertEqual(_read_ahead(token, inport), [_quote, ['+', 2, 3]])

        # atom
        inport = _InPort(io.StringIO('+'))
        token = inport.next_token()
        self.assertEqual(_read_ahead(token, inport), _Symbol('+'))

        # fail to tokenize
        inport = _InPort(io.StringIO(')'))
        token = inport.next_token()
        self.assertRaisesRegex(SyntaxError, "unexpected \)", _read_ahead, token, inport)

        # fail to tokenize
        inport = _InPort(io.StringIO('(+ 2 3'))
        token = inport.next_token()
        self.assertRaisesRegex(SyntaxError, "unexpected EOF in list", _read_ahead, token, inport)

    def test_read(self):
        # test only EOF
        inport = _InPort(io.StringIO(''))
        eof = _read(inport)
        self.assertIsInstance(eof, _Symbol)
        self.assertEqual(eof, _eof_object)

    def test_parse(self):
        inport = '(+ 2 3)'
        self.assertEqual(_parse(inport), ['+', 2, 3])

        inport = _InPort(io.StringIO('(+ 2 3)'))
        self.assertEqual(_parse(inport), ['+', 2, 3])

    def test_readchar(self):
        inport = _InPort(io.StringIO('a'))
        self.assertEqual(_readchar(inport), 'a')
        self.assertEqual(_readchar(inport), _eof_object)

    def test_to_string(self):
        self.assertEqual(_to_string(True), '#t')
        self.assertEqual(_to_string(False), '#f')
        self.assertEqual(_to_string(_Symbol('x')), 'x')
        self.assertEqual(_to_string("string"), '"string"')
        self.assertEqual(_to_string([1, 2, 3]), '(1 2 3)')
        self.assertEqual(_to_string(2+3j), '(2+3i)')
        self.assertEqual(_to_string(1), '1')

    def test_require(self):
        x = []
        self.assertRaisesRegex(SyntaxError, "() wrong length", _require, x, x!=[])

    def test_expand(self):
        # constant => unchanged
        self.assertEqual(_expand(3), 3)

        # (quote exp)
        self.assertEqual(_expand([_quote, [1, 2]]), [_quote, [1, 2]])

        # (if t c) => (if t c None)
        self.assertEqual(_expand([_if, True, 2]), [_if, True, 2, None])

        # (define (f args) body) => (define f (lambda (args) body))
        self.assertEqual(_expand([_define, [_Symbol('func'), _Symbol('x')],
                                  [_Symbol('*'), _Symbol('x'), _Symbol('x')]]),
                         [_define, _Symbol('func'), [_lambda, [_Symbol('x')],
                                                     [_Symbol('*'), _Symbol('x'), _Symbol('x')]]])

        # (begin) => None
        self.assertEqual(_expand([_begin]), None)

        # (lambda (x) e1 e2) => (lambda (x) (begin e1 e2))
        self.assertEqual(_expand([_lambda, [_Symbol('x')],
                                  [_Symbol('*'), _Symbol('x'), _Symbol('x')],
                                  [_Symbol('+'), _Symbol('x'), _Symbol('x')]]),
                         [_lambda, [_Symbol('x')],
                          [_begin,
                           [_Symbol('*'), _Symbol('x'), _Symbol('x')],
                           [_Symbol('+'), _Symbol('x'), _Symbol('x')]]])
