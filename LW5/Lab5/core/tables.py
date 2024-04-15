from core.language import *
from dataclasses import dataclass


@dataclass()
class LiteralTableItem:
    itemId: int
    itemType: Language.LiteralTypes
    itemValue: str


@dataclass()
class VariableTableItem:
    itemId: int
    itemBlockId: int
    itemBlockLevel: int
    itemName: str
    itemType: Language.VariableTypes or []


@dataclass()
class LexTableItem:
    itemType: Language.LexemeTypes
    itemValue: int or Language.KeyWords or Language.Delimiters or Language.Operators
    coordinate_line: int
    coordinate_offset: int


class LiteralTable:
    def __init__(self):
        self.Literals = []
        self.LiteralToTableItem = {}

    def push(self, value, type) -> int:
        if value in self.LiteralToTableItem:
            return self.LiteralToTableItem.get(value).itemId

        id = len(self.Literals)
        table_item = LiteralTableItem(id, type, value)

        self.Literals.append(table_item)
        self.LiteralToTableItem[value] = table_item

        return id

    def get(self, id) -> LiteralTableItem:
        return self.Literals[id]
