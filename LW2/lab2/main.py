from lexical_analyzer import LexicalAnalyzer
from tabulate import tabulate


if __name__ == '__main__':
    with open('input.cpp', 'r', encoding='utf-8') as file:
        text = file.read()

    result = LexicalAnalyzer.analyze(text)

    headers = ['Number', 'Category', 'Value']

    with open("output.txt", "w", encoding='utf-8') as output_file:
        import sys
        sys.stdout = output_file

        print(tabulate(list(result), headers=headers))

        sys.stdout = sys.__stdout__
