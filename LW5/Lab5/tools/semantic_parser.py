from core.errors import *
from core.tree import *


class SemanticParser:
    """
        Python semantic analyzer designed to perform syntax tree analysis.
    """

    def __init__(self, file_name, tree_root, literal_table, variable_table):
        """
            Initializes the semantic parser object which can parse syntax tree and define its problems.
        """

        # File provided to analysis
        self.Source = file_name
        self.Tree = tree_root

        # Environment, constants and variables
        self.LiteralTable = literal_table
        self.VariableTable = variable_table
        self.Environment = {
            "Libraries": [],
            "Namespaces": [],
            "Functions": {},
            "Variables": {}
        }

        self.AnalyzeTree(self.Tree)

    def AnalyzeTree(self, node):
        """
            Analyzes the given node and searches for semantic errors.
        """

        # Check if we meet dead-end
        if node is None:
            return

        # Get lexeme children if there are
        children = node.GetChildren()

        # Update parser environment using tree node
        self.UpdateEnvironment(node)

        # Define parser behaviour
        if node.GetLexeme() is not None:
            lexeme = node.GetLexeme()

            # Check for cout / cin
            if lexeme.itemValue in [Language.KeyWords.CIN, Language.KeyWords.COUT, Language.KeyWords.ENDL]:
                if not self.Environment["Libraries"].__contains__("iostream"):
                    raise SemanticError("iostream library required.", self.Source,
                                         lexeme.coordinate_line, lexeme.coordinate_offset)
                if not self.Environment["Namespaces"].__contains__("std"):
                    raise SemanticError("std namespace required.", self.Source,
                                         lexeme.coordinate_line, lexeme.coordinate_offset)

            # Check for using undefined var in assignment and cout
            if lexeme.itemValue == Language.Operators.EQUAL:
                right_part = children[len(children) - 1].GetLexeme()
                if right_part and right_part.itemType == Language.LexemeTypes.IDENTIFIER:
                    self.CheckForDefined(right_part)
            elif lexeme.itemValue == Language.KeyWords.COUT:
                for child in children:
                    ch_lexeme = child.GetLexeme()
                    if ch_lexeme.itemType == Language.LexemeTypes.IDENTIFIER:
                        self.CheckForDefined(ch_lexeme)

            # Check for 0 in division
            if lexeme.itemValue == Language.Operators.SLASH:
                if children[1].GetLexeme().itemType in [Language.LexemeTypes.INT_NUM, Language.LexemeTypes.DOUBLE_NUM]:
                    self.CheckForNull(children[1])

            # Check for 0 in percentage
            if lexeme.itemValue == Language.Operators.PERCENT:
                self.CheckPercentageStatement(children[0])
                self.CheckPercentageStatement(children[1])

                if children[1].GetLexeme().itemType in [Language.LexemeTypes.INT_NUM, Language.LexemeTypes.DOUBLE_NUM]:
                    self.CheckForNull(children[1])

        # Check function call
        elif node.Type == SyntaxTreNodeTypes.FUNCTION_CALL:
            function_name = self.VariableTable[children[0].GetLexeme().itemValue].itemName
            arguments_node = children[1].GetChildren()

            # Check valid amount of arguments
            if len(arguments_node) != len(self.Environment["Functions"][function_name]["Arguments"]):
                if len(arguments_node) > len(self.Environment["Functions"][function_name]["Arguments"]):
                    len_err = "many"
                else:
                    len_err = "few"
                raise SemanticError(f"Too {len_err} arguments to function {function_name}", self.Source,
                                    arguments_node[0].GetLexeme().coordinate_line,
                                    arguments_node[0].GetLexeme().coordinate_offset)

            for i in range(len(arguments_node)):
                # Get function's argument lexeme
                argument = arguments_node[i].GetLexeme()

                if argument.itemType == Language.LexemeTypes.IDENTIFIER:
                    # Check if argument is defined
                    self.CheckForDefined(argument)

                # Check if argument has valid type
                self.CheckArgumentType(function_name, argument, i)



        for child in children:
            self.AnalyzeTree(child)

    def UpdateEnvironment(self, node):
        """
            Updates semantic parser environment using info from tree nods.
        """

        # Get lexeme children if there are
        children = node.GetChildren()

        if node.GetLexeme() is not None:
            # Add libraries to parser environment
            if node.GetLexeme().itemValue == Language.KeyWords.INCLUDE:
                self.Environment["Libraries"].append(self.VariableTable[children[0].GetLexeme().itemValue].itemName)

            # Add namespaces to parser environment
            if node.GetLexeme().itemValue == Language.KeyWords.NAMESPACE:
                self.Environment["Namespaces"].append(self.VariableTable[children[0].GetLexeme().itemValue].itemName)

            if node.GetLexeme().itemValue == Language.Operators.EQUAL:
                for i in range(len(children)):
                    if children[i].Type == SyntaxTreNodeTypes.FUNCTION_CALL:
                        continue
                    elif children[i].GetLexeme().itemType == Language.LexemeTypes.IDENTIFIER and i != len(children) - 1:
                        variable = self.GetVariable(children[i].GetLexeme().itemValue)
                        variable_name = f"{str(variable.itemName)} " \
                                        f"[{str(variable.itemBlockId)}:{str(variable.itemBlockLevel)}]"
                        self.Environment["Variables"][variable_name] = "defined"


        else:
            # Add functions to parser environment
            if node.Type == SyntaxTreNodeTypes.FUNCTION_DECLARATION:
                arguments_node = children[2]
                arguments = []
                if arguments_node.GetChildren():
                    for arg in arguments_node.GetChildren():
                        variable = self.GetVariable(arg.GetChildren()[1].GetLexeme().itemValue)
                        arguments.append(variable.itemType)

                        variable_name = f"{str(variable.itemName)} " \
                                        f"[{str(variable.itemBlockId)}:{str(variable.itemBlockLevel)}]"
                        self.Environment["Variables"][variable_name] = "defined"
                function_name = self.GetVariable(children[1].GetLexeme().itemValue).itemName
                function_info = {
                    "Type": children[0].GetLexeme().itemValue,
                    "Arguments": arguments
                }

                self.Environment["Functions"][function_name] = function_info

    def CheckForDefined(self, lexeme):
        """
            Checks if variable initialized.
        """

        variable = self.GetVariable(lexeme.itemValue)
        variable_name = f"{str(variable.itemName)} " \
                        f"[{str(variable.itemBlockId)}:{str(variable.itemBlockLevel)}]"
        if self.Environment["Variables"].get(variable_name) is None:
            raise VariableUndefinedError(variable.itemName, self.Source,
                                         lexeme.coordinate_line, lexeme.coordinate_offset)

    def CheckArgumentType(self, function_name, argument, pos):
        """
            Checks function call statement.
        """

        required_type = self.Environment["Functions"][function_name]["Arguments"][pos]
        argument_type = None

        if argument.itemType == Language.LexemeTypes.IDENTIFIER:
            argument_type = self.GetVariable(argument.itemValue).itemType
        else:
            # Parse the literal type.
            if argument.itemType == Language.LexemeTypes.INT_NUM:
                argument_type = Language.VariableTypes.INT
            if argument.itemType == Language.LexemeTypes.DOUBLE_NUM:
                argument_type = Language.VariableTypes.DOUBLE
            if argument.itemType == Language.LexemeTypes.STRING:
                argument_type = Language.VariableTypes.STRING
            if argument.itemType == Language.LexemeTypes.KEY_WORD and \
                    argument.itemValue in [Language.KeyWords.TRUE, Language.KeyWords.FALSE]:
                argument_type = Language.VariableTypes.BOOL

        # Check for the array type
        if isinstance(argument_type, list) and isinstance(required_type, list):
            if argument_type[1] != required_type[1]:
                raise FunctionArgumentError(required_type, argument_type, self.Source,
                                            argument.coordinate_line, argument.coordinate_offset)

            if argument_type[0] != required_type[0]:
                if argument_type[0] == Language.VariableTypes.ARRAY \
                        and required_type[0] == Language.VariableTypes.POINTER:
                    return
                else:
                    raise FunctionArgumentError(required_type, argument_type, self.Source,
                                                argument.coordinate_line, argument.coordinate_offset)
        elif (argument_type != required_type) or argument_type is None:
            if argument.itemType == Language.LexemeTypes.OPERATOR and \
                required_type in [Language.VariableTypes.BOOL, Language.VariableTypes.INT, Language.VariableTypes.DOUBLE]:
                return
            raise FunctionArgumentError(required_type, argument_type, self.Source,
                                        argument.coordinate_line, argument.coordinate_offset)

    def CheckPercentageStatement(self, node):
        """
            Checks arithmetic problems in provided syntax tree node.
        """

        if node is None:
            return

        # Get current lexeme
        lexeme = node.GetLexeme()

        if lexeme is not None:
            if lexeme.itemType == Language.LexemeTypes.DOUBLE_NUM:
                raise SemanticError("Int was expected in percentage statement.",
                                    self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)
            if lexeme.itemType == Language.LexemeTypes.IDENTIFIER \
                    and self.GetVariable(lexeme.itemValue).itemType == Language.VariableTypes.DOUBLE:
                raise SemanticError("Int was expected in percentage statement.",
                                    self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

        for child in node.GetChildren():
            self.CheckPercentageStatement(child)

    def CheckForNull(self, node):
        """
            Checks provided literal node for null value.
        """

        lexeme = node.GetLexeme()

        # Get literal from table
        literal = self.LiteralTable.get(lexeme.itemValue)

        if lexeme.itemType == Language.LexemeTypes.INT_NUM:
            if int(literal.itemValue) == 0:
                raise DivisionByZeroError(self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

        elif lexeme.itemType == Language.LexemeTypes.DOUBLE_NUM:
            if float(literal.itemValue) == 0.0:
                raise DivisionByZeroError(self.Source, lexeme.coordinate_line, lexeme.coordinate_offset)

    def GetVariable(self, variable_id):
        """
            Gets variable item from the table.
        """

        variable = None

        try:
            variable = [v for v in self.VariableTable if v.itemId == variable_id][0]
        except:
            raise ValueError("Bad variable id")

        return variable
