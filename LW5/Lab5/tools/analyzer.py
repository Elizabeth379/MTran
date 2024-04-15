from core.tables import *
from core.checks import *
from core.errors import LexicalAnalyzerError


class LexicalAnalyzer:
    """
        Python lexical analyzer designed to perform CPP code analysis.
    """

    def __init__(self, file_name, literal_table, variable_table):
        """
            Initializes the lexical analyzer object which can perform the analysis of the provided CPP file.
        """

        # File provided to analysis
        self.Source = file_name
        self.File = open(self.Source, 'r')

        # Lexemes list
        self.Lexemes = []

        # Tables for constants and variables
        self.LiteralTable = literal_table
        self.VariableTable = variable_table

        # Analyzer variables
        self.State = Language.States.START
        self.Char = ''
        self.IsArray = False
        self.Buffer = ''
        self.CoordinateLine = 0
        self.CoordinateOffset = 0
        self.BlockLevel = 0
        self.BlockId = 0
        self.Scope = [(self.BlockLevel, self.BlockId)]
        self.ErrorMessage = ''

        # Perform analysis of provided file
        self.StartAnalysis()

    def StartAnalysis(self):
        """
            Core function of the analyzer: performs the analysis of provided CPP file.
        """

        # Read next char of the line
        self.ReadChar()

        # Analyzer state handler
        while True:
            if self.State == Language.States.START:
                self.CheckState()
            elif self.State == Language.States.ID_OR_KEY_WORD:
                self.Id_KeywordState()
            elif self.State == Language.States.NUMBER:
                self.NumberState()
            elif self.State == Language.States.DELIMITER:
                self.DelimiterState()
            elif self.State == Language.States.OPERATOR:
                self.OperatorState()
            elif self.State == Language.States.STRING:
                self.StringState()
            elif self.State == Language.States.ONE_LINE_COMMENT:
                self.OneLineCommentState()
            elif self.State == Language.States.ERROR:
                self.ErrorState()
            elif self.State == Language.States.END:
                return

    def ReadChar(self):
        """
            Reads next char in file line and corrects analyzer coordinates.
        """

        if self.Char == '\n' and self.IsArray is False:
            self.CoordinateLine += 1
            self.CoordinateOffset = 0
        elif self.Char == '{':
            self.EnterBlock()
        elif self.Char == '}':
            self.ExitBlock()
        elif self.Char == ']':
            self.IsArray = False
        elif self.Char == '\n' and self.IsArray is True:
            self.ErrorMessage = 'missing terminating ] character'
            self.ErrorState()
        else:
            self.CoordinateOffset += 1
        self.Char = self.File.read(1)

    def AddLexeme(self, type, value):
        """
            Define lexeme coordinates and adds it to the list.
        """

        if type in [Language.LexemeTypes.IDENTIFIER, Language.LexemeTypes.STRING,
                    Language.LexemeTypes.INT_NUM, Language.LexemeTypes.DOUBLE_NUM]:
            offset = self.CoordinateOffset - len(self.Buffer)
        else:
            offset = self.CoordinateOffset

        self.Lexemes.append(LexTableItem(type, value, self.CoordinateLine + 1, offset + 1))

    def AddToVariables(self, name):
        """
            Tries to find variable in the table, if not adds it to the table.
        """

        # Assign approximate scope values
        block_level = self.Scope[-1][0]
        block_id = self.Scope[-1][1]

        # Find possible existing function arguments with the same name
        filtered_vars = [var for var in self.VariableTable if
                         var.itemName == name and var.itemBlockId == 0 and var.itemBlockLevel == 0]
        if filtered_vars:
            last_var = max(filtered_vars, key=lambda x: x.itemId)
            last_var.itemBlockId = block_id
            last_var.itemBlockLevel = block_level

        # Find if variable already exists in the table
        for i in range(len(self.VariableTable)):
            if self.VariableTable[i].itemName == name\
                    and self.VariableTable[i].itemBlockId == block_id:
                return i

        # Add variable to the table
        self.VariableTable.append(VariableTableItem(len(self.VariableTable),
                                                    block_id, block_level, name, Language.VariableTypes.UNKNOWN))

        return len(self.VariableTable) - 1

    def AddToLiterals(self, value, type):
        """
            Adds literal to the table.
        """

        return self.LiteralTable.push(value, type)

    def GetLexemes(self):
        """
            Get all lexemes found in the provided code.
        """

        return self.Lexemes

    def EnterBlock(self):
        """
            Change scope values for the entering code block.
        """

        self.BlockLevel += 1
        self.BlockId += 1
        self.Scope.append((self.BlockLevel, self.BlockId))

    def ExitBlock(self):
        """
            Change scope values for the exiting code block.
        """

        self.BlockLevel -= 1
        self.Scope.pop()

    def CheckState(self):
        """
            Analyses the current char and defines its category by changing the analyzer state.
        """

        # Read the line till we meet the non-whitespace character
        while IsWhitespace(self.Char):
            self.ReadChar()

        # Define character properties and set the proper analyzer state
        if self.Char.isalpha() or self.Char == '_' or self.Char == '#':
            self.State = Language.States.ID_OR_KEY_WORD
        elif self.Char.isdigit() or self.Char == '.':
            self.State = Language.States.NUMBER
        elif IsDelimiter(self.Char):
            self.State = Language.States.DELIMITER
        elif self.Char == '"':
            self.State = Language.States.STRING
        elif IsEOF(self.Char):
            self.State = Language.States.END
        elif self.Char == ']' and self.IsArray:
            self.IsArray = False
        else:
            self.State = Language.States.OPERATOR

    def Id_KeywordState(self):
        """
            Reads the whole lexeme and decides whether it is a keyword or a variable.
        """

        self.Buffer = ''

        # Read chars till we meet the whitespace
        while self.Char.isalnum() or self.Char == '_' or self.Char == "#":
            self.Buffer += self.Char
            self.ReadChar()

        if IsOperator(self.Buffer):
            self.AddLexeme(Language.LexemeTypes.OPERATOR, operators[self.Buffer])
        elif IsKeyword(self.Buffer):
            self.AddLexeme(Language.LexemeTypes.KEY_WORD, key_words[self.Buffer])
        else:
            if self.Char == '[':
                self.IsArray = True
            id = self.AddToVariables(self.Buffer)
            self.AddLexeme(Language.LexemeTypes.IDENTIFIER, id)

        self.State = Language.States.START

    def NumberState(self):
        """
            Reads the whole lexeme, defines it type and adds it to the list.
        """

        self.Buffer = ''
        dots = 0

        # Read the whole number
        while self.Char.isdigit() or self.Char == '.':
            if self.Char == '.':
                # Multiple dots error handler
                if dots == 1:
                    return self.ThrowError('too many decimal points in number')
                dots += 1
            self.Buffer += self.Char
            self.ReadChar()

        # Unknown characters after number error handler
        if not IsWhitespace(self.Char) and self.Char not in operators \
                and not IsEOF(self.Char) and self.Char not in [')', ']', ',', ';', '}', 'e', 'E']:
            return self.ThrowError("wrong characters after a number")
        # Reset array switch
        if self.Char == ']':
            self.IsArray = False

        # Check if number is double and define lexeme and literal types
        if dots == 1:
            literal_type = Language.LiteralTypes.DOUBLE_CONSTANT
            lexeme_type = Language.LexemeTypes.DOUBLE_NUM
        else:
            literal_type = Language.LiteralTypes.INT_CONSTANT
            lexeme_type = Language.LexemeTypes.INT_NUM

        id = self.AddToLiterals(self.Buffer, literal_type)
        self.AddLexeme(lexeme_type, id)

        self.State = Language.States.START

    def ThrowError(self, error_message):
        """
            Handles error throwing.
        """

        self.ErrorMessage = error_message
        self.State = Language.States.ERROR
        return

    def DelimiterState(self):
        """
            Defines delimiter and adds lexeme to the list.
        """

        self.AddLexeme(Language.LexemeTypes.DELIMITER, delimiters[self.Char])
        self.ReadChar()
        self.State = Language.States.START

    def StringState(self):
        """
            Reads the whole lexeme and adds it to the list
        """

        self.Buffer = ''
        self.ReadChar()
        while self.Char != '"':
            # Handle unclosed quotes error
            if self.Char == '\n' or IsEOF(self.Char):
                return self.ThrowError('missing terminating " character')

            if self.Char == '\\':
                self.ReadChar()
                # Handle escape sequence error
                try:
                    self.Buffer += IsEscapeSequence(self.Char)
                except ValueError:
                    self.ErrorMessage = 'no such escape sequence'
                    self.CoordinateOffset -= 1
                    self.State = Language.States.ERROR
                    return
            else:
                self.Buffer += self.Char

            self.ReadChar()

        id = self.AddToLiterals(self.Buffer, Language.LiteralTypes.STRING_CONSTANT)
        self.AddLexeme(Language.LexemeTypes.STRING, id)
        self.ReadChar()
        self.State = Language.States.START

    def OperatorState(self):
        """
            Defines operator and adds lexeme to the list
        """

        self.Buffer = ''
        first_symbol = self.Char
        self.Buffer += self.Char
        self.ReadChar()
        self.Buffer += self.Char

        # Check for commented code and add more-than-one-symbol operator to the lexemes
        if IsOperator(self.Buffer):
            if self.Buffer == '//':
                self.State = Language.States.ONE_LINE_COMMENT
                self.ReadChar()
                return

            self.AddLexeme(Language.LexemeTypes.OPERATOR, operators[self.Buffer])
            self.ReadChar()
            self.State = Language.States.START
            return

        if IsOperator(first_symbol):
            self.AddLexeme(Language.LexemeTypes.OPERATOR, operators[first_symbol])
            self.State = Language.States.START
            return

        self.ErrorMessage = "unknown character"
        self.CoordinateOffset -= 1
        self.State = Language.States.ERROR

    def OneLineCommentState(self):
        """
            Skips the commented code.
        """
        while not (self.Char == '\n' or IsEOF(self.Char)):
            self.ReadChar()
        self.State = Language.States.START

    def ErrorState(self):
        """
            Raises analyzer error with set properties.
        """
        raise LexicalAnalyzerError(self.ErrorMessage, self.Source, self.CoordinateLine + 1, self.CoordinateOffset + 1)
