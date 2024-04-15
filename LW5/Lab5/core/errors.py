# Lexical analyzer errors
class LexicalAnalyzerError(Exception):
    """
        Error to specify lexical analysis failed.
    """

    def __init__(self, message, file_name, coordinate_line, coordinate_offset):
        self.ErrorMessage = f'File "{file_name}" [{str(coordinate_line)}:{str(coordinate_offset)}]: error: {message}'
        super().__init__(self.ErrorMessage)


# Tree parser errors
class ParserError(Exception):
    """
        Error to specify parser failed.
    """

    def __init__(self, message, file_name, coordinate_line, coordinate_offset):
        self.ErrorMessage = f'File "{file_name}" [{str(coordinate_line)}:{str(coordinate_offset)}]: error: {message}'
        super().__init__(self.ErrorMessage)


class ExpectedError(ParserError):
    """
        Error to specify parser failed on expected.
    """

    def __init__(self, expected, file_name, coordinate_line, coordinate_offset):
        super().__init__(
            f"{expected} was expected here.",
            file_name,
            coordinate_line,
            coordinate_offset,
        )


class UsingBeforeDeclarationError(ParserError):
    """
        Error to specify parser failed on unknown variable used.
    """

    def __init__(self, var_name, file_name, coordinate_line, coordinate_offset):
        super().__init__(
            f"Variable {var_name} using before declaration.",
            file_name,
            coordinate_line,
            coordinate_offset,
        )


class DoubleDeclarationError(ParserError):
    """
        Error to specify parser failed on variable declared twice.
    """

    def __init__(self, var_name, file_name, coordinate_line, coordinate_offset):
        super().__init__(
            f"Redeclaration of variable {var_name}.",
            file_name,
            coordinate_line,
            coordinate_offset,
        )


class SemanticError(Exception):
    """
        Error to specify semantic parser failed.
    """

    def __init__(self, message, file_name, coordinate_line, coordinate_offset):
        self.ErrorMessage = f'File "{file_name}" [{str(coordinate_line)}:{str(coordinate_offset)}]: error: {message}'
        super().__init__(self.ErrorMessage)


class DivisionByZeroError(SemanticError):
    def __init__(self, file_name, coordinate_line, coordinate_offset):
        super().__init__("Division by zero is forbidden.", file_name, coordinate_line, coordinate_offset)

class FunctionArgumentError(SemanticError):
    """
        Error to specify parser failed on bad function argument type index.
    """

    def __init__(self, req_type, arg_type, file_name, coordinate_line, coordinate_offset):
        super().__init__(
            f"Argument with {req_type} type was expected here, but {arg_type} got instead.",
            file_name,
            coordinate_line,
            coordinate_offset,
        )

class VariableUndefinedError(SemanticError):
    """
        Error to specify parser failed on undefined variable.
    """

    def __init__(self, var_name, file_name, coordinate_line, coordinate_offset):
        super().__init__(
            f"Variable {var_name} is undefined.",
            file_name,
            coordinate_line,
            coordinate_offset,
        )
