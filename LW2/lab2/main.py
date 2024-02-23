import re

tokens = [
    ('CLASS', r'(?<=\bclass\s)([a-zA-Z_]\w*)\b'),
    ('DATA_TYPE', r'\b(bool|signed char|short|long|long long|int|float|double|char|void|unsigned char|unsigned short|'
                  r'unsigned int|unsigned long|unsigned long long|long double|wchar_t|char8_t|char16_t|char32_t|string|'
                  r'uint32_t|size_t)\b'),
    ('KEYWORD', r'\b(if|else|while|for|return|class|struct|using|namespace|system|break|continue|do|switch|case|'
                r'default|std::swap|private|public|protected|const|override|virtual|typename|typedef|template|'
                r'delete|malloc|calloc|realloc|sizeof|NULL|printf|new|static|operator|this|friend|auto|nullptr|'
                r'try|catch|exception|setlocale)\b'),
    ('PREPROCESSOR_DIRECTIVE', r'#include'),
    ('STANDARD_LIBRARY', r'<\w+>'),
    ('COMMA', r','),
    ('END_OF_CONSTRUCTION', r';'),
    ('OUTPUT', r'cout'),
    ('NAMESPACE', r'std'),
    ('OUTPUT_MANIPULATOR', r'endl'),
    ('MACRO', r'#\w+'),
    ('COMMENT', r'//.*|/\*.*?\*/'),
    ('PARENTHESIS', r'[\(\)\{\}\[\]]'),
    ('ARROW_POINTER', r'->'),
    ('COLON', r':'),
    ('DOUBLE_COLON', r'::'),
    ('BITWISE_OPERATOR', r'[\^|]'),
    ('OPERATOR', r'([.*<>&~]|>>|<<)'),
    ('LOGICAL_OPERATOR', r'(&&|\|\||!)'),
    ('COMPARISON_OPERATOR', r'(==|!=|>=|<=)'),
    ('ARITHMETIC_OPERATOR', r'(\+\+|\-\-|\+=|-=|\*=|/=|%=|[-+/=%])'),
    ('TERNARY_OPERATOR', r'\?'),
    ('ASSIGMENT_OPERATOR', r'='),
    ('STREAM_CLASS', r'\b(ifstream|ofstream|ostream|iostream)\b'),
    ('STANDARD_FUNCTION', r'\b(strcpy|strlen|strcat|strstr|strtok|sprintf|strcmp|strchr|strrchr)\b'),
    ('MATH_FUNCTION', r'\b(pow|sqrt|sin|cos|log|exp|round)\b'),
    ('CONTAINER', r'\b(vector|list|map|unordered_map|multimap|deque|queue|stack|set|unordered_set|multiset|bitset)\b'),
    ('SPECIAL_SYMBOL', r'[#$№@]'),
    ('HEADER_FILE', r'\b[a-zA-Z_]\w*\.h\b'),
    ('CLASS_CREATION_OBJECT', r'\b[A-Z][a-zA-Z]*\s'),
    ('CONSTRUCTOR', r'\b[A-Z][a-zA-Z]*\b'),
    ('VARIABLE', r'[a-zA-Z_]\w*'),
]


def tokenize(code):
    token_regex = '|'.join('(?P<%s>%s)' % pair for pair in tokens)
    for match in re.finditer(token_regex, code):
        for name, value in match.groupdict().items():
            if value is not None:
                yield name, value


def write_to_output(tokens):
    with open("output.txt", "w") as output_file:
        output_file.write("Number\t\tElement\t\tCategory\n")
        for idx, (token_type, value) in enumerate(tokens, 1):
            output_file.write(f"{idx}\t\t\t{value}\t\t\t{token_type}\n")


if __name__ == "__main__":
    with open("input.cpp", "r") as input_file:
        code = input_file.read()

    tokens = list(tokenize(code))

    write_to_output(tokens)
