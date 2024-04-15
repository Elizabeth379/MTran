from core.checks import IsKeyword
from core.language import *
from core.tables import VariableTableItem


class SyntaxTreNodeTypes(Enum):
    COMMON = 0
    DECLARATION = 1
    FUNCTION_DECLARATION = 2
    FUNCTION_ARGUMENTS = 3
    FUNCTION_CALL = 4
    CODE_BLOCK = 5


class SyntaxTreeNode:
    def __init__(self, lexeme, type=SyntaxTreNodeTypes.COMMON):
        self.Lexeme = lexeme
        self.Children = []
        self.Type = type

    def AddChild(self, node):
        self.Children.append(node)

    def GetChildren(self):
        return self.Children

    def GetLexeme(self):
        return self.Lexeme

    def __str__(self):
        if self.Lexeme is None:
            return str(self.Type)
        elif self.Lexeme.itemType in [
            Language.LexemeTypes.IDENTIFIER,
            Language.LexemeTypes.INT_NUM,
            Language.LexemeTypes.DOUBLE_NUM
        ]:
            return f"{str(self.Lexeme.itemType)} : {str(self.Lexeme.itemValue)}"
        elif self.Lexeme.itemType == Language.LexemeTypes.STRING:
            return f"{str(self.Lexeme.itemType)} : {repr(self.Lexeme.itemValue)}"
        elif type(self.Lexeme) is VariableTableItem:
            return str(self.Lexeme.itemName)
        else:
            return str(self.Lexeme.itemValue)


def printSyntaxTree(root, depth: int = 0):
    if root is None:
        return

    print('\t' * depth + str(root))
    for child in root.GetChildren():
        # Skip types
        if child and child.GetLexeme() and str(child.GetLexeme().itemValue) \
                in ["KeyWords.VOID", "KeyWords.INT", "KeyWords.DOUBLE", "KeyWords.STRING", "KeyWords.BOOL"]:
            continue
        printSyntaxTree(child, depth + 1)
