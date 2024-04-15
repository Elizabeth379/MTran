from core.language import Language

key_words = {
    'int': Language.KeyWords.INT,
    'double': Language.KeyWords.DOUBLE,
    'bool': Language.KeyWords.BOOL,
    'string': Language.KeyWords.STRING,
    'void': Language.KeyWords.VOID,
    'true': Language.KeyWords.TRUE,
    'false': Language.KeyWords.FALSE,
    'nullptr': Language.KeyWords.NULLPTR,
    'while': Language.KeyWords.WHILE,
    'continue': Language.KeyWords.CONTINUE,
    'break': Language.KeyWords.BREAK,
    'if': Language.KeyWords.IF,
    'else': Language.KeyWords.ELSE,
    'auto': Language.KeyWords.AUTO,
    'case': Language.KeyWords.CASE,
    'const': Language.KeyWords.CONST,
    'default': Language.KeyWords.DEFAULT,
    'do': Language.KeyWords.DO,
    'enum': Language.KeyWords.ENUM,
    'extern': Language.KeyWords.EXTERN,
    'for': Language.KeyWords.FOR,
    'goto': Language.KeyWords.GOTO,
    'register': Language.KeyWords.REGISTER,
    'return': Language.KeyWords.RETURN,
    'sizeof': Language.KeyWords.SIZEOF,
    'static': Language.KeyWords.STATIC,
    'struct': Language.KeyWords.STRUCT,
    'typedef': Language.KeyWords.TYPEDEF,
    'union': Language.KeyWords.UNION,
    'volatile': Language.KeyWords.VOLATILE,
    '#include': Language.KeyWords.INCLUDE,
    'using': Language.KeyWords.USING,
    'namespace': Language.KeyWords.NAMESPACE,
    'cin': Language.KeyWords.CIN,
    'cin::': Language.KeyWords.CIN,
    'cout': Language.KeyWords.COUT,
    'cout::': Language.KeyWords.COUT,
    'exit': Language.KeyWords.EXIT,
    'endl': Language.KeyWords.ENDL,
}

delimiters = {
    '(': Language.Delimiters.OPEN_PARENTHESIS,
    ')': Language.Delimiters.CLOSE_PARENTHESIS,
    ',': Language.Delimiters.COMMA,
    ';': Language.Delimiters.SEMICOLON,
    '{': Language.Delimiters.OPEN_BRACES,
    '}': Language.Delimiters.CLOSE_BRACES,
    '[': Language.Delimiters.LEFT_BRACKET,
    ']': Language.Delimiters.RIGHT_BRACKET
}

operators = {
    '++': Language.Operators.INCREMENT,
    '--': Language.Operators.DECREMENT,
    '==': Language.Operators.DOUBLE_EQUAL,
    '!=': Language.Operators.NOT_EQUAL,
    '<=': Language.Operators.LESS_EQUAL,
    '>': Language.Operators.GREATER,
    '>=': Language.Operators.GREATER_EQUAL,
    '*=': Language.Operators.MULTIPLY_ASSIGN,
    '/=': Language.Operators.DIVIDE_ASSIGN,
    '%=': Language.Operators.PERCENT_ASSIGN,
    '&=': Language.Operators.BITWISE_AND_ASSIGN,
    '|=': Language.Operators.BITWISE_OR_ASSIGN,
    '&&': Language.Operators.LOGICAL_AND,
    'and': Language.Operators.LOGICAL_AND,
    '||': Language.Operators.LOGICAL_OR,
    'or': Language.Operators.LOGICAL_OR,
    '&': Language.Operators.BITWISE_AND,
    '|': Language.Operators.BITWISE_OR,
    '^': Language.Operators.BITWISE_XOR,
    '~': Language.Operators.BITWISE_NOT,
    '<<': Language.Operators.LEFT_SHIFT,
    '>>': Language.Operators.RIGHT_SHIFT,
    '+=': Language.Operators.ADD_ASSIGN,
    '-=': Language.Operators.SUBTRACT_ASSIGN,
    '<': Language.Operators.LESS,
    '*': Language.Operators.MULTIPLY,
    '/': Language.Operators.SLASH,
    '//': Language.Operators.DOUBLE_SLASH,
    '%': Language.Operators.PERCENT,
    '+': Language.Operators.PLUS,
    '-': Language.Operators.MINUS,
    '!': Language.Operators.NOT,
    'not': Language.Operators.NOT,
    '=': Language.Operators.EQUAL
}


def IsKeyword(lexeme):
    """
        Checks provided lexeme if it is a keyword.
    """

    return lexeme in key_words


def IsDelimiter(lexeme):
    """
        Checks provided lexeme if it is a delimiter.
    """

    return lexeme in delimiters


def IsOperator(lexeme):
    """
        Checks provided lexeme if it is an operator.
    """

    return lexeme in operators


def IsWhitespace(whitespace):
    """
        Checks provided char if it is an any kind of whitespace.
    """

    return whitespace in [' ', '\n', '\t']


def IsEOF(EOF):
    """
        Checks provided char if it is an eof.
    """

    return EOF == ''


def IsEscapeSequence(char):
    """
        Checks provided char if it is a part of escape sequence.
    """

    if char == 'a':
        return '\a'
    elif char == 'b':
        return '\b'
    elif char == 'f':
        return '\f'
    elif char == 'n':
        return '\n'
    elif char == 'r':
        return '\r'
    elif char == 't':
        return '\t'
    elif char == 'v':
        return '\v'
    elif char == "'":
        return "\'"
    elif char == '"':
        return '\"'
    elif char == '\\':
        return '\\'
    else:
        raise ValueError("No such escape sequence")


def IsVariableType(key_word):
    """
        Checks provided keyword if it is a variable type.
    """

    return key_word in [Language.KeyWords.INT, Language.KeyWords.DOUBLE, Language.KeyWords.BOOL,
                        Language.KeyWords.STRING, Language.KeyWords.VOID]


def IsAdditionOperator(operator):
    """
        Checks provided operator if it is an addition operator: plus or minus.
    """

    return operator in [Language.Operators.PLUS, Language.Operators.MINUS]


def IsMultiplicationOperator(operator):
    """
        Checks provided operator if it is a multiplication operator: asterisk, slash or percent.
    """

    return operator in [Language.Operators.MULTIPLY, Language.Operators.SLASH, Language.Operators.PERCENT]

inverted_operators = {
    Language.Operators.DOUBLE_EQUAL: '==',
    Language.Operators.NOT_EQUAL: '!=',
    Language.Operators.LESS_EQUAL: '<=',
    Language.Operators.GREATER: '>',
    Language.Operators.GREATER_EQUAL: '>=',
    Language.Operators.MULTIPLY_ASSIGN: '*=',
    Language.Operators.DIVIDE_ASSIGN: '/=',
    Language.Operators.PERCENT_ASSIGN: '%=',
    Language.Operators.BITWISE_AND_ASSIGN: '&=',
    Language.Operators.BITWISE_OR_ASSIGN: '|=',
    Language.Operators.LOGICAL_AND: 'and',
    Language.Operators.LOGICAL_OR: 'or',
    Language.Operators.BITWISE_AND: '&',
    Language.Operators.BITWISE_OR: '|',
    Language.Operators.BITWISE_XOR: '^',
    Language.Operators.BITWISE_NOT: '~',
    Language.Operators.LEFT_SHIFT: '<<',
    Language.Operators.RIGHT_SHIFT: '>>',
    Language.Operators.ADD_ASSIGN: '+=',
    Language.Operators.SUBTRACT_ASSIGN: '-=',
    Language.Operators.LESS: '<',
    Language.Operators.MULTIPLY: '*',
    Language.Operators.SLASH: '/',
    Language.Operators.DOUBLE_SLASH: '//',
    Language.Operators.PERCENT: '%',
    Language.Operators.PLUS: '+',
    Language.Operators.MINUS: '-',
    Language.Operators.NOT: 'not',
    Language.Operators.EQUAL: '='
}

