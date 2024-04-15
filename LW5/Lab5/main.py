from tools.analyzer import *
from tools.translator import *
from tools.tree_parser import *
from tools.semantic_parser import *


def br():
    """
        Prints text separator.
    """
    print('\n', '#' * 130, '\n')


def printLexemes(lexemes, filename="lexer_output.txt"):
    """
    Formats the lexemes output and writes it to a file.
    """

    with open(filename, 'w') as file:
        file.write("{:<10} {:<32} {:<20}\n".format('   POS', ' ' * 14 + 'TYPE', ' ' * 8 + 'VALUE'))
        file.write("{:<10} {:<32} {:<20}\n".format('-' * 10, '-' * 32, '-' * 20))

        for lexeme in lexemes:
            if lexeme.coordinate_offset < 10:
                coordinate = f'[{str(lexeme.coordinate_line)}:0{str(lexeme.coordinate_offset)}]'
            else:
                coordinate = f'[{str(lexeme.coordinate_line)}:{str(lexeme.coordinate_offset)}]'

            lexeme_type = str(lexeme.itemType)
            if lexeme.itemType in [Language.LexemeTypes.STRING, Language.LexemeTypes.INT_NUM,
                                   Language.LexemeTypes.DOUBLE_NUM]:
                value = f'Constant-ID: {str(lexeme.itemValue)}'
            elif lexeme.itemType == Language.LexemeTypes.IDENTIFIER:
                value = f'Identifier-ID: {str(lexeme.itemValue)}'
            else:
                value = str(lexeme.itemValue)

            file.write("{:<10} {:<32} {:<20}\n".format(coordinate, lexeme_type, value))


def printLiterals(literals):
    """
        Beautifies the literals output and prints it.
    """

    print("{:<4} {:<32} {:<20}".format(' ID', ' ' * 14 + 'TYPE', ' ' * 8 + 'VALUE'))
    print("{:<4} {:<32} {:<20}".format('-' * 4, '-' * 32, '-' * 20))

    for literal in literals:
        literal_id = str(literal.itemId)
        literal_type = str(literal.itemType)

        if literal.itemType == Language.LiteralTypes.STRING_CONSTANT:
            literal_value = repr(literal.itemValue)
        else:
            literal_value = str(literal.itemValue)

        print("{:<4} {:<32} {:<20}".format(literal_id, literal_type, literal_value))

    br()


def printVariables(variables):
    """
        Beautifies the variables output  and prints it.
    """

    print("{:<4} {:<20} {:<70} {:<7} {:<10}".format(' ID', ' ' * 8 + 'NAME',
                                                    ' ' * 33 + 'Type', 'ScopeId', 'ScopeLevel'))
    print("{:<4} {:<20} {:<70} {:<7} {:<10}".format('-' * 4, '-' * 20,
                                                    '-' * 70, '-' * 7, '-' * 10))

    for variable in variables:
        variable_id = str(variable.itemId)
        variable_name = str(variable.itemName)
        variable_type = str(variable.itemType)
        variable_blockId = str(variable.itemBlockId)
        variable_blockLevel = str(variable.itemBlockLevel)

        print("{:<4} {:<20} {:<70} {:<7} {:<10}".format(variable_id, variable_name,
                                                        variable_type, variable_blockId, variable_blockLevel))

    br()


def main():
    # Define the testing files name
    fileName = "main.cpp"

    # Define tables for the literals and variables
    literalTable = LiteralTable()
    variableTable = []

    try:
        # Perform lexical analysis
        lexAnalyzer = LexicalAnalyzer(fileName, literalTable, variableTable)

        # Get resulting lexemes from the analyzer
        lexemes = lexAnalyzer.GetLexemes()
        parser = TreeParser(fileName, lexemes, literalTable, variableTable)

        # Check for semantic errors
        root = parser.GetTree()
        semantic_parser = SemanticParser(fileName, root, literalTable, variableTable)

        # Clear variable table
        variableTable = [var for var in variableTable if var.itemType != Language.VariableTypes.UNKNOWN]
        br()

        # Parsed lexemes
        #print("\t⇒ LEXEMES:\n")
        printLexemes(lexemes)

        # Parsed literals
        print("\t⇒ LITERAL TABLE:\n")
        printLiterals(literalTable.Literals)

        # Parsed variables
        print("\t⇒ VARIABLE TABLE:\n")
        printVariables(variableTable)

        # Syntax tree
        print("\t⇒ Syntax tree:\n")
        parser.PrintSyntaxTree()

        # Translate CPP AST to Python
        br()
        #print("\t⇒ Translated code output:\n")
        #translator = Translator(root, literalTable, variableTable)

    except LexicalAnalyzerError as ex:
        print(ex)
    except ParserError as ex:
        print(ex)
    except SemanticError as ex:
        print(ex)

if __name__ == '__main__':
    main()
