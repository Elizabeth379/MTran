import contextlib
from core.errors import *
from core.tree import *
from core.checks import *


class TreeParser:
    """
        Python syntax tree parser designed to build up a syntax tree from lexemes provided.
    """

    def __init__(self, file_name, lexemes, literal_table, variable_table):
        """
            Initializes the syntax tree parser object which can build up a syntax tree from lexemes provide.
        """

        #  File provided to analysis
        self.Source = file_name

        #  Lexemes, constants and variables
        self.Lexemes = lexemes
        self.LiteralTable = literal_table
        self.VariableTable = variable_table

        # Parser variables
        self.CurrLexemeIndex = 0
        self.BlockLevel = 0
        self.BlockId = 0
        self.Scope = [(self.BlockLevel, self.BlockId)]
        self.Root = SyntaxTreeNode(None, SyntaxTreNodeTypes.CODE_BLOCK)
        self.NestingLoop = 0

        self.ParseLexemes()

    def ParseLexemes(self):
        """
            Core function of the parser: performs the parsing of provided lexemes and building up the syntax tree.
        """

        while self.LexemesRemaining():
            node = self.ParseStatement()
            self.Root.AddChild(node)

    def ParseStatement(self, for_cycle=False):
        """
            Parses full statement to define its type and build proper node for the tree.
        """

        # Current lexeme being parsed
        lexeme = self.GetCurrentLexeme()

        if lexeme.itemType == Language.LexemeTypes.KEY_WORD:
            if lexeme.itemValue == Language.KeyWords.INCLUDE:
                return self.ParseInclude()
            elif lexeme.itemValue == Language.KeyWords.USING:
                return self.ParseUsing()
            elif IsVariableType(lexeme.itemValue) \
                    and self.GetNeighbourLexeme(1).itemType == Language.LexemeTypes.IDENTIFIER \
                    and self.GetNeighbourLexeme(2).itemValue == Language.Delimiters.OPEN_PARENTHESIS:
                return self.ParseFunctionDeclaration()
            elif IsVariableType(lexeme.itemValue):
                return self.ParseVariableDeclaration()
            elif lexeme.itemValue == Language.KeyWords.COUT:
                return self.ParseCout()
            elif lexeme.itemValue == Language.KeyWords.CIN:
                return self.ParseCin()
            elif lexeme.itemValue == Language.KeyWords.IF:
                return self.ParseIf()
            elif lexeme.itemValue == Language.KeyWords.WHILE:
                return self.ParseWhile()
            elif lexeme.itemValue == Language.KeyWords.DO:
                return self.ParseDoWhile()
            elif lexeme.itemValue == Language.KeyWords.FOR:
                return self.ParseFor()
            elif lexeme.itemValue == Language.KeyWords.EXIT:
                return self.ParseExit()
            elif lexeme.itemValue in [Language.KeyWords.BREAK, Language.KeyWords.CONTINUE]:
                return self.ParseCycleKeywords()
            else:
                raise ParserError(
                    f"unexpected lexeme: {str(lexeme)}",
                    self.Source,
                    lexeme.coordinate_line,
                    lexeme.coordinate_offset,
                )
        elif lexeme.itemType == Language.LexemeTypes.DELIMITER:
            if lexeme.itemValue == Language.Delimiters.OPEN_BRACES:
                return self.ParseBlockCode()
            else:
                raise ParserError(
                    f"unexpected lexeme: {str(lexeme)}",
                    self.Source,
                    lexeme.coordinate_line,
                    lexeme.coordinate_offset,
                )
        elif lexeme.itemType == Language.LexemeTypes.IDENTIFIER:
            identifier_node = self.ParseUsingIdentifier()

            # Handle array member
            if self.CurrentLexemeMatches(Language.Delimiters.LEFT_BRACKET):
                identifier_node.AddChild(self.ParseArrayIndex())
                self.NextLexeme()

            if self.GetCurrentLexeme().itemValue in [Language.Operators.INCREMENT, Language.Operators.DECREMENT]:
                # Parse identifier increment/decrement
                node = SyntaxTreeNode(self.GetCurrentLexeme())
                node.AddChild(identifier_node)
                self.NextLexeme()
            elif self.CurrentLexemeMatches(Language.Delimiters.OPEN_PARENTHESIS):
                # Parse function call
                node = SyntaxTreeNode(None, SyntaxTreNodeTypes.FUNCTION_CALL)
                node.AddChild(identifier_node)
                node.AddChild(self.ParseFunctionCall())
            else:
                # Parse assignment for the identifier
                node = self.ParseAssignment(identifier_node)

            # Await ';'
            if not for_cycle:
                self.WaitForDelimiter(Language.Delimiters.SEMICOLON)
                self.NextLexeme()

            return node
        else:
            raise ParserError(
                f"unexpected lexeme: {str(lexeme)}",
                self.Source,
                lexeme.coordinate_line,
                lexeme.coordinate_offset,
            )

    def GetCurrentLexeme(self):
        """
            Returns the current lexeme being parsed.
        """

        if not self.LexemesRemaining():
            lexeme = self.Lexemes[self.CurrLexemeIndex - 1]
            raise ParserError("unexpected end of file", self.Source, lexeme.coordinate_offset, lexeme.coordinate_offset)
        return self.Lexemes[self.CurrLexemeIndex]

    def GetNeighbourLexeme(self, offset):
        """
            Returns the lexeme offset current being parsed.
        """

        if self.CurrLexemeIndex + offset >= len(self.Lexemes):
            lexeme = self.Lexemes[self.CurrLexemeIndex + offset]
            raise ParserError("unexpected end of file", self.Source, lexeme.coordinate_offset, lexeme.coordinate_offset)
        return self.Lexemes[self.CurrLexemeIndex + offset]

    def ParseInclude(self):
        """
            Parses an include statement.
        """

        # #include
        self.WaitForKeyword(Language.KeyWords.INCLUDE)
        include_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # <
        self.NextLexeme()
        self.WaitForDelimiter(Language.Operators.LESS)

        # LIBRARY
        self.NextLexeme()
        self.WaitForIdentifier()
        library = self.GetVariable(self.GetCurrentLexeme())
        library.itemType = Language.VariableTypes.LIBRARY
        library_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # >
        self.NextLexeme()
        self.WaitForDelimiter(Language.Operators.GREATER)

        self.NextLexeme()
        include_node.AddChild(library_node)

        return include_node

    def ParseUsing(self):
        """
            Parses a using statement.
        """

        # using
        self.WaitForKeyword(Language.KeyWords.USING)
        using_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # namespace
        self.NextLexeme()
        self.WaitForKeyword(Language.KeyWords.NAMESPACE)
        namespace_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # NAMESPACE_NAME
        self.NextLexeme()
        self.WaitForIdentifier()
        namespace = self.GetVariable(self.GetCurrentLexeme())
        namespace.itemType = Language.VariableTypes.NAMESPACE
        namespace_name_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # ;
        self.NextLexeme()
        self.WaitForDelimiter(Language.Delimiters.SEMICOLON)

        self.NextLexeme()
        namespace_node.AddChild(namespace_name_node)
        using_node.AddChild(namespace_node)

        return using_node

    def ParseFunctionDeclaration(self):
        """
            Parses the function declaration statement and its body.
        """

        self.EnterBlock()

        # Function type
        type_node, var_type = self.ParseVariableType()

        # Function name
        identifier_node = self.ParseDeclareIdentifier(var_type)
        self.GetVariable(identifier_node.GetLexeme()).itemBlockLevel -= 1
        self.GetVariable(identifier_node.GetLexeme()).itemBlockId = 0

        # Function declaration statement
        declaration_node = SyntaxTreeNode(None, SyntaxTreNodeTypes.FUNCTION_DECLARATION)
        declaration_node.AddChild(type_node)
        declaration_node.AddChild(identifier_node)

        # (
        self.NextLexeme()

        # Function arguments
        arguments_node = SyntaxTreeNode(None, SyntaxTreNodeTypes.FUNCTION_ARGUMENTS)
        if not self.CurrentLexemeMatches(Language.Delimiters.CLOSE_PARENTHESIS):
            while self.GetNeighbourLexeme(-1).itemValue != Language.Delimiters.CLOSE_PARENTHESIS:
                arguments_node.AddChild(self.ParseVariableDeclaration(True))
        else:
            # )
            self.NextLexeme()

        declaration_node.AddChild(arguments_node)

        # Function body
        declaration_node.AddChild(self.ParseBlockCode(var_type[1]))

        # Exiting function scope
        self.ExitBlock()

        return declaration_node

    def ParseFunctionCall(self):
        """
            Parses the function call statement.
        """

        # (
        self.WaitForDelimiter(Language.Delimiters.OPEN_PARENTHESIS)
        self.NextLexeme()

        call_node = SyntaxTreeNode(None, SyntaxTreNodeTypes.FUNCTION_ARGUMENTS)
        while not self.CurrentLexemeMatches(Language.Delimiters.CLOSE_PARENTHESIS):
            argument_node = None

            # Try to get INT / DOUBLE argument
            with contextlib.suppress(ParserError):
                argument_node = self.ParseArithmeticExpr()

            # Try to get STRING argument
            if argument_node is None:
                if self.GetNeighbourLexeme(-1).itemType == Language.LexemeTypes.IDENTIFIER:
                    self.CurrLexemeIndex -= 1
                with contextlib.suppress(ParserError):
                    argument_node = self.ParseStringExpr()

            # Try to get BOOL argument
            if argument_node is None:
                if self.GetNeighbourLexeme(-1).itemType == Language.LexemeTypes.IDENTIFIER:
                    self.CurrLexemeIndex -= 1
                with contextlib.suppress(ParserError):
                    argument_node = self.ParseBoolExpr()

            if argument_node is None:
                raise ParserError("unknown function argument type", self.Source,
                                  self.GetCurrentLexeme().coordinate_line, self.GetCurrentLexeme().coordinate_offset)
            else:
                call_node.AddChild(argument_node)

            if not self.CurrentLexemeMatches(Language.Delimiters.CLOSE_PARENTHESIS):
                # ,
                self.WaitForDelimiter(Language.Delimiters.COMMA)
                self.NextLexeme()

        # )
        self.WaitForDelimiter(Language.Delimiters.CLOSE_PARENTHESIS)
        self.NextLexeme()

        return call_node

    def ParseVariableDeclaration(self, function_declaration=False):
        """
            Parses a variable declaration statement.
        """

        # Variable type
        type_node, var_type = self.ParseVariableType()

        # Variable name
        identifier_node = self.ParseDeclareIdentifier(var_type)

        # Handle array declaration
        if self.CurrentLexemeMatches(Language.Delimiters.LEFT_BRACKET):
            identifier_node.AddChild(self.ParseArrayIndex())
            self.NextLexeme()

        # Variable declaration statement
        declaration_node = SyntaxTreeNode(None, SyntaxTreNodeTypes.DECLARATION)
        declaration_node.AddChild(type_node)

        # Parse if there is a variable init after declaration
        identifier_node = self.ParseOptVarInit(identifier_node)

        declaration_node.AddChild(identifier_node)

        # Expected delimiter depending on variable type
        if function_declaration is not True:
            while self.CurrentLexemeMatches(Language.Delimiters.COMMA):
                self.NextLexeme()

                # Type correction
                if (
                    self.GetNeighbourLexeme(1).itemValue
                    == Language.Delimiters.LEFT_BRACKET
                ):
                    var_type = [Language.VariableTypes.ARRAY, var_type]

                elif isinstance(var_type, list):
                    var_type = var_type[1]
                # Variable name
                identifier_node = self.ParseDeclareIdentifier(var_type)

                # Parse if there is a variable init after declaration
                identifier_node = self.ParseOptVarInit(identifier_node)

                # Handle array declaration
                if self.CurrentLexemeMatches(Language.Delimiters.LEFT_BRACKET):
                    identifier_node.AddChild(self.ParseArrayIndex())
                    self.NextLexeme()

                # Add additional identifier child
                declaration_node.AddChild(identifier_node)

            self.WaitForDelimiter(Language.Delimiters.SEMICOLON)
        elif self.GetNeighbourLexeme(1).itemValue == Language.Delimiters.CLOSE_PARENTHESIS:
            self.WaitForDelimiter(Language.Delimiters.COMMA)
        self.NextLexeme()

        return declaration_node

    def ParseOptVarInit(self, identifier_node):
        """
            Parses a variable init if there is in declaration statement.
        """

        if not self.LexemesRemaining() or not self.CurrentLexemeMatches(Language.Operators.EQUAL):
            return identifier_node

        return self.ParseAssignment(identifier_node)

    def ParseVariableType(self):
        """
            Parses a variable type statement.
        """

        type_lexeme = self.GetCurrentLexeme()
        type_node = SyntaxTreeNode(type_lexeme)
        var_type = Language.VariableTypes.UNKNOWN

        # Define correct variable type

        if type_lexeme.itemValue == Language.KeyWords.INT:
            var_type = Language.VariableTypes.INT
        elif type_lexeme.itemValue == Language.KeyWords.DOUBLE:
            var_type = Language.VariableTypes.DOUBLE
        elif type_lexeme.itemValue == Language.KeyWords.STRING:
            var_type = Language.VariableTypes.STRING
        elif type_lexeme.itemValue == Language.KeyWords.BOOL:
            var_type = Language.VariableTypes.BOOL
        elif type_lexeme.itemValue == Language.KeyWords.VOID:
            var_type = Language.VariableTypes.VOID
        else:
            raise ParserError("unknown variable type",
                              self.Source, type_lexeme.coordinate_line, type_lexeme.coordinate_offset)

        # Add subType:
        if self.GetNeighbourLexeme(1).itemType == Language.LexemeTypes.IDENTIFIER \
                and self.GetNeighbourLexeme(2).itemValue == Language.Delimiters.OPEN_PARENTHESIS:
            var_type = [Language.VariableTypes.FUNCTION, var_type]
        elif self.GetNeighbourLexeme(1).itemValue == Language.Operators.MULTIPLY:
            self.NextLexeme()
            var_type = [Language.VariableTypes.POINTER, var_type]
        elif self.GetNeighbourLexeme(1).itemValue == Language.Operators.BITWISE_AND:
            self.NextLexeme()
            var_type = [Language.VariableTypes.REFERENCE, var_type]
        elif self.GetNeighbourLexeme(2).itemValue == Language.Delimiters.LEFT_BRACKET:
            var_type = [Language.VariableTypes.ARRAY, var_type]

        # Switch to variable name
        self.NextLexeme()

        return type_node, var_type

    def ParseDeclareIdentifier(self, var_type):
        """
            Parses a variable name statement.
        """

        # Check if current lexeme is a variable name
        self.WaitForIdentifier()

        lexeme = self.GetCurrentLexeme()
        node = SyntaxTreeNode(lexeme)
        curr_var = self.GetVariable(lexeme)

        # Set scope for the variable
        block_level = self.Scope[-1][0]
        block_id = self.Scope[-1][1]

        if curr_var.itemType not in [Language.VariableTypes.UNKNOWN]:
            # Check for the double declaration of the variable
            for var in self.VariableTable:
                if curr_var.itemName == var.itemName and block_id == var.itemBlockId:
                    raise DoubleDeclarationError(curr_var.itemName,
                                                 self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

            self.VariableTable.append(VariableTableItem(len(self.VariableTable), block_id,
                                                        block_level, curr_var.itemName, var_type))
            curr_var = self.VariableTable[-1]
            lexeme.itemValue = len(self.VariableTable) - 1

        # Setup correct variable data
        curr_var.itemType = var_type
        curr_var.itemBlockLevel = block_level
        curr_var.itemBlockId = block_id

        self.NextLexeme()

        return node

    def ParseBlockCode(self, function_type=None):
        """
            Parses a block of code.
        """

        # Check for the '{'
        self.WaitForDelimiter(Language.Delimiters.OPEN_BRACES)
        self.NextLexeme()

        # If we outside the function declaration open new scope
        if function_type is None:
            self.EnterBlock()

        code_block_node = SyntaxTreeNode(None, SyntaxTreNodeTypes.CODE_BLOCK)

        # Parse the lexemes of the block
        while self.LexemesRemaining() and \
                not self.CurrentLexemeMatches(Language.Delimiters.CLOSE_BRACES) \
                and not self.CurrentLexemeMatches(Language.KeyWords.RETURN):
            code_block_node.AddChild(self.ParseStatement())

        # Check for the '}'
        if function_type:
            code_block_node.AddChild(self.ParseReturn(function_type))

        self.WaitForDelimiter(Language.Delimiters.CLOSE_BRACES)
        self.NextLexeme()

        # If we outside the function declaration close new scope
        if function_type is None:
            self.ExitBlock()

        return code_block_node

    def ParseUsingIdentifier(self):
        """
            Checks identifier to be used.
        """

        # Check current lexeme for identifier
        self.WaitForIdentifier()

        lexeme = self.GetCurrentLexeme()
        node = SyntaxTreeNode(lexeme)

        var = self.GetVariable(lexeme)

        # Check variable if it is declared: by searching for it in the table
        var_real_id = -1

        for scope in reversed(self.Scope):
            block_level = scope[0]
            block_id = scope[1]

            # Search for variable in selected scope by name
            searched_var = None
            if filtered_vars := [
                v
                for v in self.VariableTable
                if v.itemName == var.itemName and v.itemBlockId == block_id and v.itemBlockLevel == block_level
                   and v.itemType != Language.VariableTypes.UNKNOWN
            ]:
                searched_var = max(filtered_vars, key=lambda x: x.itemId)

            # Prevent using undefined variables
            if searched_var is None or \
                    searched_var.itemType == Language.VariableTypes.UNKNOWN:
                continue

            # Try to get variable id
            with contextlib.suppress(ValueError):
                var_real_id = self.VariableTable.index(searched_var)
                break

        if var_real_id < 0:
            raise UsingBeforeDeclarationError(var.itemName, self.Source,
                                              lexeme.coordinate_line, lexeme.coordinate_offset)

        lexeme.itemValue = var_real_id
        self.NextLexeme()

        return node

    def ParseAssignment(self, identifier_node):
        """
            Parses full assignment statement to build proper node for the tree.
        """

        # Await for the '='
        self.WaitForOperator(Language.Operators.EQUAL)
        equal_lexeme = self.GetCurrentLexeme()
        equal_node = SyntaxTreeNode(equal_lexeme)
        equal_node.AddChild(identifier_node)

        # Parse multiple assignment
        while self.CurrentLexemeMatches(Language.Operators.EQUAL):

            # Switch to the right assignment part
            self.NextLexeme()

            # Get type of the left part of the assignment
            identifier_lexeme = identifier_node.GetLexeme()
            var = self.GetVariable(identifier_lexeme)
            var_type = var.itemType

            right_node = None

            # Parse literals inside left part error of multiple assignment
            if self.GetNeighbourLexeme(1).itemValue == Language.Operators.EQUAL and \
                self.GetCurrentLexeme().itemType != Language.LexemeTypes.IDENTIFIER:
                raise ParserError("Identifier required as left operand of multiple assignment.", self.Source,
                                  identifier_lexeme.coordinate_line, identifier_lexeme.coordinate_offset)
            if var_type in [Language.VariableTypes.INT, Language.VariableTypes.DOUBLE]:
                right_node = self.ParseArithmeticExpr()
            if isinstance(var.itemType, list) \
                    and var_type[0] in [Language.VariableTypes.POINTER, Language.VariableTypes.ARRAY]:
                if var_type[1] in [Language.VariableTypes.INT, Language.VariableTypes.DOUBLE]:
                    right_node = self.ParseArithmeticExpr()
                elif var_type[1] == Language.VariableTypes.STRING:
                    right_node = self.ParseStringExpr()
                elif var_type[1] == Language.VariableTypes.BOOL:
                    right_node = self.ParseBoolExpr()
            elif var_type == Language.VariableTypes.STRING:
                right_node = self.ParseStringExpr()
            elif var_type == Language.VariableTypes.BOOL:
                right_node = self.ParseBoolExpr()
            else:
                ParserError("Unknown type of identifier.", self.Source,
                            identifier_lexeme.coordinate_line, identifier_lexeme.coordinate_offset)

            # Add right assignment part to the assignment node
            equal_node.AddChild(right_node)

        return equal_node

    def ParseArithmeticExpr(self):
        """
            Parses an arithmetic expression.
        """

        left_node = self.ParseUnaryAndNode()

        while self.LexemesRemaining() and IsAdditionOperator(self.GetCurrentLexeme().itemValue):
            lexeme = self.GetCurrentLexeme()
            op_node = self.ParseOperator(lexeme.itemValue)
            right_node = self.ParseMultNode()
            op_node.AddChild(left_node)
            op_node.AddChild(right_node)
            left_node = op_node

        return left_node

    def ParseUnaryAndNode(self):
        """
            Parses a unary operator if exists and addition expression node.
        """

        lexeme = self.GetCurrentLexeme()
        op_node = None
        if IsAdditionOperator(lexeme.itemValue):
            op_node = self.ParseOperator(lexeme.itemValue)

        node = self.ParseMultNode()

        if op_node is None:
            return node

        op_node.AddChild(node)
        return op_node

    def ParseMultNode(self):
        """
            Parses the multiplication expression if it is.
        """

        left_node = self.ParseExprNode()

        while self.LexemesRemaining() and IsMultiplicationOperator(self.GetCurrentLexeme().itemValue):
            lexeme = self.GetCurrentLexeme()
            op_node = self.ParseOperator(lexeme.itemValue)
            right_node = self.ParseExprNode()
            op_node.AddChild(left_node)
            op_node.AddChild(right_node)
            left_node = op_node

        return left_node

    def ParseExprNode(self):
        """
            Parses an expression node and defines it.
        """

        lexeme = self.GetCurrentLexeme()
        function_call = lexeme.itemType == Language.LexemeTypes.IDENTIFIER and \
                isinstance(self.GetVariable(lexeme).itemType, list) and \
                self.GetVariable(lexeme).itemType[0] == Language.VariableTypes.FUNCTION

        if self.CurrentLexemeMatches(Language.Delimiters.OPEN_PARENTHESIS):
            self.NextLexeme()
            node = self.ParseArithmeticExpr()
            self.WaitForDelimiter(Language.Delimiters.CLOSE_PARENTHESIS)
            self.NextLexeme()
        elif lexeme.itemType in [Language.LexemeTypes.INT_NUM, Language.LexemeTypes.DOUBLE_NUM]:
            node = SyntaxTreeNode(lexeme)
            self.NextLexeme()
        elif lexeme.itemType == Language.LexemeTypes.IDENTIFIER \
                and self.GetNeighbourLexeme(1).itemValue == Language.Delimiters.LEFT_BRACKET:
            # Array identifier
            node = self.ParseUsingIdentifier()

            # Array index
            node.AddChild(self.ParseArrayIndex())
            self.NextLexeme()
        elif function_call:
            node = self.ParseStatement(True)
            if self.GetNeighbourLexeme(1).itemValue == Language.Delimiters.SEMICOLON:
                self.NextLexeme()
        elif lexeme.itemType == Language.LexemeTypes.IDENTIFIER:
            node = self.ParseUsingIdentifier()
            self.WaitForVariableType(node.GetLexeme(), (Language.VariableTypes.INT, Language.VariableTypes.DOUBLE))
        else:
            raise ExpectedError("number", self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

        return node

    def ParseStringExpr(self, cout=False):
        """
            Parses a string expression.
        """

        left_node = self.ParseStringNode(cout)

        while self.LexemesRemaining() and self.CurrentLexemeMatches(Language.Operators.PLUS):
            op_node = self.ParseOperator(Language.Operators.PLUS)
            right_node = self.ParseStringNode(cout)
            op_node.AddChild(left_node)
            op_node.AddChild(right_node)
            left_node = op_node

        return left_node

    def ParseStringNode(self, cout=False):
        """
            Parses a string node.
        """

        lexeme = self.GetCurrentLexeme()
        if lexeme.itemType == Language.LexemeTypes.IDENTIFIER and \
                isinstance(self.GetVariable(lexeme).itemType, list) and \
                self.GetVariable(lexeme).itemType[0] == Language.VariableTypes.FUNCTION:
            node = self.ParseStatement(True)
            self.NextLexeme()
        elif lexeme.itemType == Language.LexemeTypes.IDENTIFIER:
            node = self.ParseUsingIdentifier()
            if not cout:
                self.WaitForVariableType(node.GetLexeme(), Language.VariableTypes.STRING)

            # Handle array index
            if self.CurrentLexemeMatches(Language.Delimiters.LEFT_BRACKET):
                node.AddChild(self.ParseArrayIndex())
                self.NextLexeme()
        elif lexeme.itemValue == Language.KeyWords.ENDL:
            # endl keyword handler
            node = SyntaxTreeNode(self.GetCurrentLexeme())
            self.NextLexeme()
        else:
            self.WaitForStringValue()
            node = SyntaxTreeNode(lexeme)
            self.NextLexeme()

        return node

    def ParseArrayIndex(self):
        """
            Parse an array index expression.
        """

        # [
        self.WaitForDelimiter(Language.Delimiters.LEFT_BRACKET)

        # Array Index
        self.NextLexeme()
        node = self.ParseArithmeticExpr()

        # ]
        self.WaitForDelimiter(Language.Delimiters.RIGHT_BRACKET)

        return node

    def ParseOperator(self, op):
        """
            Creates operator-based node.
        """

        self.WaitForOperator(op)
        op_node = SyntaxTreeNode(self.GetCurrentLexeme())
        self.NextLexeme()

        return op_node

    def ParseIf(self):
        """
            Parses full if statement to build proper node for the tree.
        """

        # if
        self.WaitForKeyword(Language.KeyWords.IF)

        if_node = SyntaxTreeNode(self.GetCurrentLexeme())
        self.NextLexeme()

        # (
        self.WaitForDelimiter(Language.Delimiters.OPEN_PARENTHESIS)
        self.NextLexeme()

        # if-condition error handler
        if self.CurrentLexemeMatches(Language.Delimiters.CLOSE_PARENTHESIS):
            lexeme = self.GetCurrentLexeme()
            raise ExpectedError("bool expression", self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

        # Parse condition statement
        condition_node = self.ParseBoolExpr()

        # )
        self.WaitForDelimiter(Language.Delimiters.CLOSE_PARENTHESIS)
        self.NextLexeme()

        # Parse if body
        if_statement_node = self.ParseStatement()

        if_node.AddChild(condition_node)
        if_node.AddChild(if_statement_node)

        # Parse else body if exists
        if self.LexemesRemaining() and self.CurrentLexemeMatches(Language.KeyWords.ELSE):
            self.NextLexeme()
            else_statement_node = self.ParseStatement()
            if_node.AddChild(else_statement_node)

        return if_node

    def ParseBoolExpr(self):
        """
            Parses full bool condition to build proper node for the tree.
        """

        left_node = self.ParseBoolExpr_And()

        while self.LexemesRemaining() and self.CurrentLexemeMatches(Language.Operators.LOGICAL_OR):
            or_node = self.ParseOperator(Language.Operators.LOGICAL_OR)
            right_node = self.ParseBoolExpr_And()
            or_node.AddChild(left_node)
            or_node.AddChild(right_node)
            left_node = or_node

        return left_node

    def ParseBoolExpr_And(self):
        """
            Parses full bool condition: &&(logical_and).
        """

        left_node = self.ParseBoolExpr_Not()

        while self.LexemesRemaining() and self.CurrentLexemeMatches(Language.Operators.LOGICAL_AND):
            and_node = self.ParseOperator(Language.Operators.LOGICAL_AND)
            right_node = self.ParseBoolExpr_Not()
            and_node.AddChild(left_node)
            and_node.AddChild(right_node)
            left_node = and_node

        return left_node

    def ParseBoolExpr_Not(self):
        """
             Parses full bool condition: !(logical_not).
        """

        was_not = False
        not_node = None

        if self.CurrentLexemeMatches(Language.Operators.NOT):
            not_node = self.ParseOperator(Language.Operators.NOT)
            was_not = True

        node = self.ParseBoolExpr_Term()
        if not was_not:
            return node

        not_node.AddChild(node)

        return not_node

    def ParseBoolExpr_Term(self):
        """
             Parses full bool condition: identifier.
        """

        lexeme = self.GetCurrentLexeme()
        if lexeme.itemType == Language.LexemeTypes.IDENTIFIER and \
                isinstance(self.GetVariable(lexeme).itemType, list) and \
                self.GetVariable(lexeme).itemType[0] == Language.VariableTypes.FUNCTION:
            node = self.ParseStatement(True)
            self.NextLexeme()
        elif lexeme.itemType == Language.LexemeTypes.IDENTIFIER and \
                self.GetVariable(lexeme).itemType == Language.VariableTypes.BOOL:
            node = self.ParseUsingIdentifier()
        elif self.GetCurrentLexeme().itemType == Language.LexemeTypes.INT_NUM:
            node = self.ParseArithmeticExpr()
        elif self.CurrentLexemeMatches(Language.Delimiters.OPEN_PARENTHESIS):
            old_lex_index = self.CurrLexemeIndex
            self.NextLexeme()

            try:
                node = self.ParseBoolExpr()
                self.WaitForDelimiter(Language.Delimiters.CLOSE_PARENTHESIS)
                self.NextLexeme()
            except ParserError:
                self.CurrLexemeIndex = old_lex_index
                node = self.ParseComparison()
        elif lexeme.itemValue in (Language.KeyWords.TRUE, Language.KeyWords.FALSE):
            node = self.ParseBoolExpr_Literal()
        else:
            node = self.ParseComparison()

        return node

    def ParseComparison(self):
        """
            Parses comparison expression.
        """

        # Left comparison part
        lexeme = self.GetCurrentLexeme()
        left_node, left_type = self.ParseComparisonNode()

        # Comparison operator
        self.WaitForComparisonOperator()
        op_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # Right comparison part
        self.NextLexeme()
        right_node, right_type = self.ParseComparisonNode()

        if left_type != right_type:
            raise ParserError(
                f"Can't compare {str(left_type)} and {str(right_type)}",
                self.Source,
                lexeme.coordinate_line,
                lexeme.coordinate_offset,
            )

        op_node.AddChild(left_node)
        op_node.AddChild(right_node)

        return op_node

    def ParseComparisonNode(self):
        """
            Parses a comparison node.
        """

        lexeme = self.GetCurrentLexeme()
        old_lex_index = self.CurrLexemeIndex

        try:
            node = self.ParseArithmeticExpr()
            return node, Language.ComparisonTypes.ARITHMETIC
        except ExpectedError:
            self.CurrLexemeIndex = old_lex_index
            try:
                node = self.ParseStringExpr()

                return node, Language.ComparisonTypes.STRING
            except ExpectedError as e:
                raise ExpectedError(
                    "arithmetic or string expression",
                    self.Source,
                    lexeme.coordinate_line,
                    lexeme.coordinate_offset,
                ) from e

    def ParseBoolExpr_Literal(self):
        """
             Parses full bool condition: literal.
        """

        self.WaitForBoolValue()
        node = SyntaxTreeNode(self.GetCurrentLexeme())
        self.NextLexeme()

        return node

    def ParseWhile(self):
        """
            Parses a while loop statement.
        """

        # while
        self.WaitForKeyword(Language.KeyWords.WHILE)
        while_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # (
        self.NextLexeme()
        self.WaitForDelimiter(Language.Delimiters.OPEN_PARENTHESIS)

        # Empty condition exception handler
        self.NextLexeme()
        if self.CurrentLexemeMatches(Language.Delimiters.CLOSE_PARENTHESIS):
            lexeme = self.GetCurrentLexeme()
            raise ExpectedError("bool expression", self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

        # while condition
        condition_node = self.ParseBoolExpr()
        while_node.AddChild(condition_node)

        # )
        self.WaitForDelimiter(Language.Delimiters.CLOSE_PARENTHESIS)
        self.NextLexeme()

        # Check for the empty cycle body
        if self.CurrentLexemeMatches(Language.Delimiters.SEMICOLON):
            return while_node

        # Parse body of the cycle
        self.NestingLoop += 1
        statement_node = self.ParseStatement()
        self.NestingLoop -= 1

        while_node.AddChild(statement_node)

        return while_node

    def ParseFor(self):
        """
            Parses a for loop statement.
        """

        # for
        self.WaitForKeyword(Language.KeyWords.FOR)
        for_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # (
        self.NextLexeme()
        self.WaitForDelimiter(Language.Delimiters.OPEN_PARENTHESIS)

        # Empty condition exception handler
        self.NextLexeme()
        if self.CurrentLexemeMatches(Language.Delimiters.CLOSE_PARENTHESIS):
            lexeme = self.GetCurrentLexeme()
            raise ExpectedError("bool expression", self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

        # for condition
        # Possible var used
        if not self.CurrentLexemeMatches(Language.Delimiters.SEMICOLON):
            for_node.AddChild(self.ParseStatement())

        # Possible break condition
        if not self.CurrentLexemeMatches(Language.Delimiters.SEMICOLON):
            for_node.AddChild(self.ParseBoolExpr())

        # Possible variable change
        self.NextLexeme()
        if not self.CurrentLexemeMatches(Language.Delimiters.CLOSE_PARENTHESIS):
            for_node.AddChild(self.ParseStatement(True))

        # )
        self.WaitForDelimiter(Language.Delimiters.CLOSE_PARENTHESIS)
        self.NextLexeme()

        # Check for the empty cycle body
        if self.CurrentLexemeMatches(Language.Delimiters.SEMICOLON):
            return for_node

        # Parse body of the cycle
        self.NestingLoop += 1
        statement_node = self.ParseStatement()
        self.NestingLoop -= 1

        for_node.AddChild(statement_node)

        return for_node

    def ParseDoWhile(self):
        """
            Parses a do-while loop statement.
        """

        # do
        self.WaitForKeyword(Language.KeyWords.DO)
        do_while_node = SyntaxTreeNode(self.GetCurrentLexeme())
        self.NextLexeme()

        # Parse body of the cycle
        self.NestingLoop += 1
        do_while_node.AddChild(self.ParseStatement())
        self.NestingLoop -= 1

        # while
        self.WaitForKeyword(Language.KeyWords.WHILE)
        while_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # (
        self.NextLexeme()
        self.WaitForDelimiter(Language.Delimiters.OPEN_PARENTHESIS)

        # Empty condition exception handler
        self.NextLexeme()
        if self.CurrentLexemeMatches(Language.Delimiters.CLOSE_PARENTHESIS):
            lexeme = self.GetCurrentLexeme()
            raise ExpectedError("bool expression", self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

        # while condition
        condition_node = self.ParseBoolExpr()
        while_node.AddChild(condition_node)

        # )
        self.WaitForDelimiter(Language.Delimiters.CLOSE_PARENTHESIS)
        self.NextLexeme()

        do_while_node.AddChild(while_node)
        self.WaitForDelimiter(Language.Delimiters.SEMICOLON)
        self.NextLexeme()

        return do_while_node

    def ParseCycleKeywords(self):
        """
            Checks if we can use specific cycle keyword.
        """

        lexeme = self.GetCurrentLexeme()
        keyword = ""

        if lexeme.itemValue == Language.KeyWords.BREAK:
            keyword = "break"
        elif lexeme.itemValue == Language.KeyWords.CONTINUE:
            keyword = "continue"

        # Error in usage handler
        if not self.IsCycleKeywordAvailable():
            raise ParserError(f"{keyword} is not available in this context.",
                              self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)
        if keyword == "break":
            self.WaitForKeyword(Language.KeyWords.BREAK)
        elif keyword == "continue":
            self.WaitForKeyword(Language.KeyWords.CONTINUE)

        # Create node with loop keyword
        node = SyntaxTreeNode(lexeme)
        self.NextLexeme()

        # ;
        self.WaitForDelimiter(Language.Delimiters.SEMICOLON)
        self.NextLexeme()

        return node

    def IsCycleKeywordAvailable(self):
        """
            Checks cycles keywords availability.
        """

        return self.NestingLoop > 0

    def ParseCin(self):
        """
            Parses a cin statement.
        """

        # cin
        self.WaitForKeyword(Language.KeyWords.CIN)
        cin_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # >>
        self.NextLexeme()
        self.WaitForDelimiter(Language.Operators.RIGHT_SHIFT)

        # In data
        while self.LexemesRemaining() and self.CurrentLexemeMatches(Language.Operators.RIGHT_SHIFT):
            self.NextLexeme()
            identifier_node = self.ParseUsingIdentifier()
            if self.CurrentLexemeMatches(Language.Delimiters.LEFT_BRACKET):
                identifier_node.AddChild(self.ParseArrayIndex())
                self.NextLexeme()
            cin_node.AddChild(identifier_node)

        # ;
        self.WaitForDelimiter(Language.Delimiters.SEMICOLON)
        self.NextLexeme()

        return cin_node

    def ParseCout(self):
        """
            Parses a cout statement.
        """

        # cout
        self.WaitForKeyword(Language.KeyWords.COUT)
        cout_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # <<
        self.NextLexeme()
        self.WaitForDelimiter(Language.Operators.LEFT_SHIFT)

        # Out data
        while self.LexemesRemaining() and self.CurrentLexemeMatches(Language.Operators.LEFT_SHIFT):
            self.NextLexeme()
            cout_node.AddChild(self.ParseStringExpr(True))

        # ;
        self.WaitForDelimiter(Language.Delimiters.SEMICOLON)
        self.NextLexeme()

        return cout_node

    def ParseExit(self):
        """
            Parses an exit statement.
        """

        # exit
        self.WaitForKeyword(Language.KeyWords.EXIT)
        exit_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # (
        self.NextLexeme()
        self.WaitForDelimiter(Language.Delimiters.OPEN_PARENTHESIS)

        # Exit code
        self.NextLexeme()
        exit_code_node = self.ParseArithmeticExpr()

        # )
        self.WaitForDelimiter(Language.Delimiters.CLOSE_PARENTHESIS)
        self.NextLexeme()

        # ;
        self.WaitForDelimiter(Language.Delimiters.SEMICOLON)
        self.NextLexeme()

        exit_node.AddChild(exit_code_node)

        return exit_node

    def ParseReturn(self, type):
        """
            Parses a return statement.
        """

        if (self.GetCurrentLexeme().itemValue == Language.Delimiters.CLOSE_BRACES and
                type == Language.VariableTypes.VOID):
            return None

        # return
        self.WaitForKeyword(Language.KeyWords.RETURN)
        return_node = SyntaxTreeNode(self.GetCurrentLexeme())

        # Return expression
        self.NextLexeme()
        if type in [Language.VariableTypes.INT, Language.VariableTypes.DOUBLE]:
            return_node.AddChild(self.ParseArithmeticExpr())
        elif type == Language.VariableTypes.BOOL:
            return_node.AddChild(self.ParseBoolExpr())
        elif type == Language.VariableTypes.STRING:
            return_node.AddChild(self.ParseStringExpr())

        # ;
        self.WaitForDelimiter(Language.Delimiters.SEMICOLON)
        self.NextLexeme()

        return return_node

    def PrintSyntaxTree(self):
        """
            Prints the syntax tree.
        """

        printSyntaxTree(self.Root)

    def GetTree(self):
        """
            Returns the syntax tree root.
        """

        return self.Root

    def NextLexeme(self):
        """
            Switches parser focus to the next lexeme.
        """

        self.CurrLexemeIndex += 1

    def WaitForKeyword(self, key_word):
        """
            Checks current lexeme if it is a keyword.
        """

        lexeme = self.GetCurrentLexeme()
        if lexeme.itemValue != key_word:
            raise ExpectedError(str(key_word), self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

    def WaitForDelimiter(self, delimiter):
        """
            Checks current lexeme if it is a delimiter.
        """

        lexeme = self.GetCurrentLexeme()
        if lexeme.itemValue != delimiter:
            raise ExpectedError(str(delimiter), self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

    def WaitForOperator(self, operator):
        """
            Checks current lexeme if it is an operator.
        """

        lexeme = self.GetCurrentLexeme()
        if lexeme.itemValue != operator:
            raise ExpectedError(str(operator), self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

    def WaitForVariableType(self, lexeme, type):
        """
            Checks current lexeme if it is a variable type.
        """

        if lexeme.itemType != Language.LexemeTypes.IDENTIFIER:
            raise ExpectedError(
                f"{str(type)} variable",
                self.Source,
                lexeme.coordinate_line,
                lexeme.coordinate_offset,
            )
        var = self.GetVariable(lexeme)
        if isinstance(type, Language.VariableTypes):
            if var.itemType != type:
                raise ExpectedError(
                    f"{str(type)} variable",
                    self.Source,
                    lexeme.coordinate_line,
                    lexeme.coordinate_offset,
                )
        elif var.itemType not in type:
            if (
                isinstance(var.itemType, list)
                and var.itemType[1] in type
            ):
                return
            raise ExpectedError(
                f"one of the following variable types: {str(type)}",
                self.Source,
                lexeme.coordinate_line,
                lexeme.coordinate_offset,
            )

    def WaitForIdentifier(self):
        """
            Checks current lexeme if it is an identifier.
        """

        lexeme = self.GetCurrentLexeme()
        if lexeme.itemType != Language.LexemeTypes.IDENTIFIER:
            raise ExpectedError("identifier", self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

    def WaitForComparisonOperator(self):
        """
            Checks current lexeme if it is a comparison operator.
        """

        lexeme = self.GetCurrentLexeme()
        if lexeme.itemValue not in [
            Language.Operators.DOUBLE_EQUAL,
            Language.Operators.NOT_EQUAL,
            Language.Operators.LESS,
            Language.Operators.LESS_EQUAL,
            Language.Operators.GREATER,
            Language.Operators.GREATER_EQUAL,
        ]:
            raise ExpectedError("One of the comparison Language.Operators",
                                self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

    def WaitForBoolValue(self):
        """
            Checks current lexeme if it is a boolean value.
        """

        lexeme = self.GetCurrentLexeme()
        if lexeme.itemValue not in [Language.KeyWords.TRUE, Language.KeyWords.FALSE]:
            raise ExpectedError("Bool literal", self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

    def WaitForStringValue(self):
        """
            Checks current lexeme if it is a string value.
        """

        lexeme = self.GetCurrentLexeme()
        if lexeme.itemType != Language.LexemeTypes.STRING:
            raise ExpectedError("String literal", self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

    def LexemesRemaining(self):
        """
            Checks if there are any remaining lexemes.
        """

        return self.CurrLexemeIndex < len(self.Lexemes)

    def GetVariable(self, lexeme):
        """
            Returns the variable associated with the lexeme.
        """

        return self.VariableTable[lexeme.itemValue]

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

    def CurrentLexemeMatches(self, type):
        """
            Checks current lexeme match.
        """

        if type in [
            Language.LexemeTypes.IDENTIFIER,
            Language.LexemeTypes.INT_NUM,
            Language.LexemeTypes.DOUBLE_NUM,
            Language.LexemeTypes.STRING,
        ]:
            return type == self.Lexemes[self.CurrLexemeIndex].itemType
        else:
            return type == self.Lexemes[self.CurrLexemeIndex].itemValue
