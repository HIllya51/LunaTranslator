from pyjsparser.pyjsparserdata import *

REGEXP_SPECIAL_SINGLE = {'\\', '^', '$', '*', '+', '?', '.'}

NOT_PATTERN_CHARS = {
    '^', '$', '\\', '.', '*', '+', '?', '(', ')', '[', ']', '|'
}  # what about '{', '}',  ???

CHAR_CLASS_ESCAPE = {'d', 'D', 's', 'S', 'w', 'W'}
CONTROL_ESCAPE_CHARS = {'f', 'n', 'r', 't', 'v'}
CONTROL_LETTERS = {
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D',
    'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
    'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
}


def SpecialChar(char):
    return {'type': 'SpecialChar', 'content': char}


def isPatternCharacter(char):
    return char not in NOT_PATTERN_CHARS


class JsRegExpParser:
    def __init__(self, source, flags):
        self.source = source
        self.flags = flags
        self.index = 0
        self.length = len(source)
        self.lineNumber = 0
        self.lineStart = 0

    def parsePattern(self):
        '''Perform sctring escape - for regexp literals'''
        return {'type': 'Pattern', 'contents': self.parseDisjunction()}

    def parseDisjunction(self):
        alternatives = []
        while True:
            alternatives.append(self.parseAlternative())
            if not self.isEOF():
                self.expect_character('|')
            else:
                break
        return {'type': 'Disjunction', 'contents': alternatives}

    def isEOF(self):
        if self.index >= self.length:
            return True
        return False

    def expect_character(self, character):
        if self.source[self.index] != character:
            self.throwUnexpected(character)
        self.index += 1

    def parseAlternative(self):
        contents = []
        while not self.isEOF() and self.source[self.index] != '|':
            contents.append(self.parseTerm())
        return {'type': 'Alternative', 'contents': contents}

    def follows(self, chars):
        for i, c in enumerate(chars):
            if self.index + i >= self.length or self.source[self.index +
                                                            i] != c:
                return False
        return True

    def parseTerm(self):
        assertion = self.parseAssertion()
        if assertion:
            return assertion
        else:
            return {
                'type': 'Term',
                'contents': self.parseAtom()
            }  # quantifier will go inside atom!

    def parseAssertion(self):
        if self.follows('$'):
            content = SpecialChar('$')
            self.index += 1
        elif self.follows('^'):
            content = SpecialChar('^')
            self.index += 1
        elif self.follows('\\b'):
            content = SpecialChar('\\b')
            self.index += 2
        elif self.follows('\\B'):
            content = SpecialChar('\\B')
            self.index += 2
        elif self.follows('(?='):
            self.index += 3
            dis = self.parseDisjunction()
            self.expect_character(')')
            content = {'type': 'Lookached', 'contents': dis, 'negated': False}
        elif self.follows('(?!'):
            self.index += 3
            dis = self.parseDisjunction()
            self.expect_character(')')
            content = {'type': 'Lookached', 'contents': dis, 'negated': True}
        else:
            return None
        return {'type': 'Assertion', 'content': content}

    def parseAtom(self):
        if self.follows('.'):
            content = SpecialChar('.')
            self.index += 1
        elif self.follows('\\'):
            self.index += 1
            content = self.parseAtomEscape()
        elif self.follows('['):
            content = self.parseCharacterClass()
        elif self.follows('(?:'):
            self.index += 3
            dis = self.parseDisjunction()
            self.expect_character(')')
            content = 'idk'
        elif self.follows('('):
            self.index += 1
            dis = self.parseDisjunction()
            self.expect_character(')')
            content = 'idk'
        elif isPatternCharacter(self.source[self.index]):
            content = self.source[self.index]
            self.index += 1
        else:
            return None
        quantifier = self.parseQuantifier()
        return {'type': 'Atom', 'content': content, 'quantifier': quantifier}

    def parseQuantifier(self):
        prefix = self.parseQuantifierPrefix()
        if not prefix:
            return None
        greedy = True
        if self.follows('?'):
            self.index += 1
            greedy = False
        return {'type': 'Quantifier', 'contents': prefix, 'greedy': greedy}

    def parseQuantifierPrefix(self):
        if self.isEOF():
            return None
        if self.follows('+'):
            content = '+'
            self.index += 1
        elif self.follows('?'):
            content = '?'
            self.index += 1
        elif self.follows('*'):
            content = '*'
            self.index += 1
        elif self.follows(
                '{'
        ):  # try matching otherwise return None and restore the state
            i = self.index
            self.index += 1
            digs1 = self.scanDecimalDigs()
            # if no minimal number of digs provided then return no quantifier
            if not digs1:
                self.index = i
                return None
            # scan char limit if provided
            if self.follows(','):
                self.index += 1
                digs2 = self.scanDecimalDigs()
            else:
                digs2 = ''
            # must be valid!
            if not self.follows('}'):
                self.index = i
                return None
            else:
                self.expect_character('}')
                content = int(digs1), int(digs2) if digs2 else None
        else:
            return None
        return content

    def parseAtomEscape(self):
        ch = self.source[self.index]
        if isDecimalDigit(ch) and ch != 0:
            digs = self.scanDecimalDigs()
        elif ch in CHAR_CLASS_ESCAPE:
            self.index += 1
            return SpecialChar('\\' + ch)
        else:
            return self.parseCharacterEscape()

    def parseCharacterEscape(self):
        ch = self.source[self.index]
        if ch in CONTROL_ESCAPE_CHARS:
            return SpecialChar('\\' + ch)
        if ch == 'c':
            'ok, fuck this shit.'

    def scanDecimalDigs(self):
        s = self.index
        while not self.isEOF() and isDecimalDigit(self.source[self.index]):
            self.index += 1
        return self.source[s:self.index]


a = JsRegExpParser('a(?=x)', '')
print(a.parsePattern())
